#include "myDetectorSD.hh"
#include "myDetectorHit.hh"

#include "G4RunManager.hh"
#include "G4HCofThisEvent.hh"
#include "G4DynamicParticle.hh"
#include "G4Step.hh"
#include "G4StepPoint.hh"
#include "G4VProcess.hh"
#include "G4ThreeVector.hh"
#include "G4TouchableHistory.hh"
#include "G4Track.hh"
#include "G4Step.hh"
#include "G4SDManager.hh"
#include "G4ios.hh"
#include "G4SystemOfUnits.hh"
#include "G4Run.hh"

#include <iostream>
#include <iomanip>
#include <string.h>
#include <fstream>

//using namespace CLHEP;

#define SIZE_DATA_BUFFER 65536
#define OUTPUT_COUNT 50

myDetectorSD::myDetectorSD(const G4String& name,
                           const G4String& hitsCollectionName)
: G4VSensitiveDetector(name), fHitsCollection(NULL), fHCID(-1)
{
  collectionName.insert(hitsCollectionName);
  fgInstance = this;  

	// flags
  fTrackHits = 1;
  fParticleFilter = 1; // only select certain particles at beginning of track 

  char outfile[50];
 
  // open output for hits
  sprintf(outfile, "%s_Hits.out", name.data());
  initHitOutfile(outfile);

  // allocate memory for hit data buffers 
  fcount_hits = 0;
  fPos = new G4ThreeVector[SIZE_DATA_BUFFER];
  fDir = new G4ThreeVector[SIZE_DATA_BUFFER];
  fKEHit = new G4double[SIZE_DATA_BUFFER]; 
  fhitNb = new G4int[SIZE_DATA_BUFFER];
  fParentID = new G4int[SIZE_DATA_BUFFER];
  fTrackID = new G4int[SIZE_DATA_BUFFER];
  fhitEventID = new G4int[SIZE_DATA_BUFFER];
  fGlobalTime = new G4double[SIZE_DATA_BUFFER];
  fLocalTime = new G4double[SIZE_DATA_BUFFER];
  fParticle = new G4String[SIZE_DATA_BUFFER];
  fProcess = new G4String[SIZE_DATA_BUFFER];
  fCreatorProcess = new G4String[SIZE_DATA_BUFFER];
  fhitRunID = new G4int[SIZE_DATA_BUFFER];

}

myDetectorSD::~myDetectorSD()
{
  // write hit data buffer to file
  if (fcount_hits > 0) outputHitData();

  // delete data buffers
  delete[] fhitEventID;
  delete[] fGlobalTime;
  delete[] fLocalTime;
  delete[] fhitNb;
  delete[] fParentID;
  delete[] fTrackID;
  delete[] fPos;
  delete[] fDir;
  delete[] fKEHit;
  delete[] fParticle;
  delete[] fProcess;
  delete[] fCreatorProcess;
  delete[] fhitRunID;

  fout_hits.close();
}

void myDetectorSD::Initialize(G4HCofThisEvent* hce)
{
  fHitsCollection = new myDetectorHitsCollection
  (SensitiveDetectorName, collectionName[0]);
  if (fHCID<0)
  { fHCID = G4SDManager::GetSDMpointer()->GetCollectionID(fHitsCollection);}
  hce->AddHitsCollection(fHCID,fHitsCollection);
}

G4bool myDetectorSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{

  // get hit information
  G4ParticleDefinition* pd = step->GetTrack()->GetDefinition();
  G4int trackID = step->GetTrack()->GetTrackID();
  G4int parentID = step->GetTrack()->GetParentID();
  G4int eventID = Instance()->GetCurrentEventID();
  G4int runID = G4RunManager::GetRunManager()->GetCurrentRun()->GetRunID();

  // ### Neutron Filter;  Flag set in myDetectorSD constructor
  if (fParticleFilter){
		// only select designated particle hits. 
    if (pd->GetParticleName() != "neutron") return false;
		// set track to be killed after first encounter 
		//step->GetTrack()->SetTrackStatus(fStopAndKill);
		step->GetTrack()->SetTrackStatus(fKillTrackAndSecondaries);
  } // ####

  // get hit information
  //G4double edep = step->GetTotalEnergyDeposit();
  G4double ke = step->GetPreStepPoint()->GetKineticEnergy();
  G4ThreeVector pos = step->GetPreStepPoint()->GetPosition();
  G4ThreeVector dir = step->GetPreStepPoint()->GetMomentumDirection();
  G4StepPoint * thePostPoint = step->GetPostStepPoint();
  G4String processName = thePostPoint->GetProcessDefinedStep()->GetProcessName();

  G4String creatorProcessName = "";
  const G4VProcess* creatorProcess = step->GetTrack()->GetCreatorProcess();
  if(!creatorProcess) 
    creatorProcessName = "";
  else 
    creatorProcessName = creatorProcess->GetProcessName();
  
  G4double globalTime = step->GetPreStepPoint()->GetGlobalTime();
  G4double localTime = step->GetTrack()->GetLocalTime();
  // add hit to collection
  myDetectorHit* newHit = new myDetectorHit();

  newHit->SetParticleDefinition(pd);
  newHit->SetKE(ke);
  newHit->SetPos(pos);
  newHit->SetDir(dir);
  newHit->SetGlobalTime(globalTime);
  newHit->SetLocalTime(localTime);
  newHit->SetProcessName(processName);
  newHit->SetCreatorProcessName(creatorProcessName);
  newHit->SetEventID(eventID);
  newHit->SetParentID(parentID);
  newHit->SetTrackID(trackID);
  newHit->SetRunID(runID);

  // insert hit into collection
  fHitsCollection->insert(newHit);

  return true;
}

void myDetectorSD::EndOfEvent(G4HCofThisEvent*)
{

  G4int nofHits = fHitsCollection->entries();
  G4ParticleDefinition *pd;
  G4double KE;
  G4int eventID;

  
  for ( G4int i=0; i<nofHits; i++ ){
    myDetectorHit *aHit = (*fHitsCollection)[i]; 
  
    eventID = aHit->GetEventID();

    // store information for hit
    if (fTrackHits == 1) {

      // get Kinetic energy of Hit
      KE = aHit->GetKE();

      // get particle definition
      pd = aHit->GetParticleDefinition();

      fKEHit[fcount_hits] = KE/eV;
      fhitNb[fcount_hits] = i;
      fhitEventID[fcount_hits] = aHit->GetEventID();
      fParentID[fcount_hits] = aHit->GetParentID();
      fTrackID[fcount_hits] = aHit->GetTrackID();
      fParticle[fcount_hits] = pd->GetParticleName();
      fProcess[fcount_hits] = aHit->GetProcessName();
      fCreatorProcess[fcount_hits] = aHit->GetCreatorProcessName();
      fPos[fcount_hits] = aHit->GetPos()/m;
      fDir[fcount_hits] = aHit->GetDir();
      fGlobalTime[fcount_hits] = aHit->GetGlobalTime()/ms;
      fLocalTime[fcount_hits] = aHit->GetLocalTime()/ms;
      fhitRunID[fcount_hits] = aHit->GetRunID();
      fcount_hits++;
    }
  }


  // if hit data buffer is full, write contents to file
  if (fcount_hits >= OUTPUT_COUNT) outputHitData();
} 

myDetectorSD* myDetectorSD::fgInstance = 0;

myDetectorSD* myDetectorSD::Instance()
{
  return fgInstance;
}

void myDetectorSD::initHitOutfile(char* outfile){

  fout_hits.open(outfile);
  fout_hits //<< setw(12) << "run"
            << setw(12) << "event" 
            //<< setw(12) << "hit"
            //<< setw(12) << "parentID"
            //<< setw(12) << "TrackID"
            //<< setw(12) << "particle"
            //<< setw(18) << "process"
            //<< setw(18) << "creator process"
            << setw(18) << "KE (eV)" 
            << setw(18) << "GlobalTime[ms]"
            //<< setw(18) << "LocalTime[ms]"
            << setw(22) << "Position[m]" 
            << setw(28) << "Direction" << endl;
}

void myDetectorSD::outputHitData(){

  for (G4int k=0; k < fcount_hits; k++){
    fout_hits //<< setw(12) << fhitRunID[k]
              << setw(12) << fhitEventID[k]
              //<< setw(12) << fhitNb[k]
              //<< setw(12) << fParentID[k]
              //<< setw(12) << fTrackID[k]
              //<< setw(12) << fParticle[k]
              //<< setw(18) << fProcess[k]
              //<< setw(18) << fCreatorProcess[k]
              << setw(18) << fKEHit[k]
              << setw(18) << fGlobalTime[k]
              //<< setw(18) << fLocalTime[k]
              << setw(9) << fPos[k]
              << setw(19) << fDir[k]
              << endl;
  }
  fcount_hits = 0;
  
  return;
}

