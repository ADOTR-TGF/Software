//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
/// \file hadronic/Hadr03/src/GammaPhysics.cc
/// \brief Implementation of the GammaPhysics class
//
// $Id: GammaPhysics.cc 66587 2012-12-21 11:06:44Z ihrivnac $
//

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#include "myGammaPhysics.hh"

#include "G4ParticleDefinition.hh"
#include "G4ProcessManager.hh"
#include "G4StepLimiter.hh"
#include "G4UserSpecialCuts.hh"

// Processes

#include "G4PhotoNuclearProcess.hh"
#include "G4CascadeInterface.hh"

#include "G4SystemOfUnits.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

myGammaPhysics::myGammaPhysics(const G4String& name)
:  G4VPhysicsConstructor(name)
{ }

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

myGammaPhysics::~myGammaPhysics()
{ }

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void myGammaPhysics::ConstructProcess()
{
   G4ProcessManager* pManager = G4Gamma::Gamma()->GetProcessManager();
   //
   G4PhotoNuclearProcess* process = new G4PhotoNuclearProcess();
   //
   G4CascadeInterface* bertini = new G4CascadeInterface(); // 0-10GeV
   bertini->SetMaxEnergy(10*GeV);
   process->RegisterMe(bertini);
   //
   pManager->AddDiscreteProcess(process);
	
	//G4StepLimiter* stepLimiter = new G4StepLimiter();
	//pManager->AddDiscreteProcess(stepLimiter);

	G4UserSpecialCuts* specialCuts = new G4UserSpecialCuts();
	pManager->AddDiscreteProcess(specialCuts);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
