#include <string>

using namespace std;

#ifndef myActionInitialization_h
#define myActionInitialization_h 1

#include "G4VUserActionInitialization.hh"

class myActionInitialization : public G4VUserActionInitialization
{
  public:
    myActionInitialization(double medianBinEnergy); //string particleInputFilename
    virtual ~myActionInitialization();

    virtual void BuildForMaster() const;
    virtual void Build() const;

	private:
		double fParticleInputFilename; //string
};

#endif
