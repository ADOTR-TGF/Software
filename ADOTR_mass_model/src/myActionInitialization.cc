#include "myActionInitialization.hh"
#include "myPrimaryGeneratorAction.hh"
#include "myRunAction.hh"
#include "myEventAction.hh"

myActionInitialization::myActionInitialization(double medianBinEnergy) //string particleInputFilename
 :  G4VUserActionInitialization()
{
		fParticleInputFilename = medianBinEnergy; //particleInputFilename
}

myActionInitialization::~myActionInitialization()
{}

void myActionInitialization::BuildForMaster() const
{
  myRunAction* runAction = new myRunAction;
  SetUserAction(runAction);
}

void myActionInitialization::Build() const
{
  SetUserAction(new myPrimaryGeneratorAction(fParticleInputFilename));
  
  myRunAction* runAction = new myRunAction;
  SetUserAction(runAction);
  
  myEventAction* eventAction = new myEventAction(runAction);
  SetUserAction(eventAction);

cout << "HEY MAN HERES THE ACTION INIT";
}
