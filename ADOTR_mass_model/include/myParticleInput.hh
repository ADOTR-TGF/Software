#ifndef myParticleInput_h
#define myParticleInput_h 1

#include <string>
#include "myParticle.hh"

using namespace std;

class myParticleInput
{

  public: 
  myParticleInput(); //string filename
    ~myParticleInput();
  double * generateParticleRands();
    
    myParticle getParticle();
	
  private:
    // input file variables
    
    long    fNinput;

    G4int* fEvent;
    G4String* fParticle;
    G4double* fEnergy;     // eV
    G4double* fArrivalTime; // ms
    double* fPosX;         // km
    double* fPosY;         // km
    double* fPosZ;         // km
		double* fDirX;        
		double* fDirY;        
		double* fDirZ;        

		double* fECD;          // empirical cumulative distribution
		double* fWeight;       

		long findx;            // pointer into last fECD bin
		long fpcount = 0l;     // current number of particles chosen
};

#endif
