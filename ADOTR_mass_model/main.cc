#include <string>
#include <fstream>
#include "myDetectorConstruction.hh"
#include "myActionInitialization.hh"
#include "myPhysicsList.hh"

using namespace std;

#ifdef G4MULTITHREADED
#include "G4MTRunManager.hh"
#else
#include "G4RunManager.hh"
#endif

#include "G4UImanager.hh"

//#ifdef G4VIS_USE
#include "G4VisExecutive.hh"
//#endif

//#ifdef G4UI_USE
#include "G4UIExecutive.hh"
//#endif

extern double binHigh, binLow;

double binHigh;
double binLow;

int main(int argc, char** argv){
	double medianBinEnergy = std::stod(argv[1]);
	//int numberInputParticles = std::stoi(argv[2]); //not needed?
	
	/*double binEnergies[] = {0.095, 0.105, 0.115, 0.125, 0.135, 0.145, 0.155, 0.165, 0.175, 0.185, 
                        0.195, 0.205, 0.215, 0.225, 0.235, 0.245, 0.260, 0.280, 0.300, 0.320, 
                        0.340, 0.360, 0.380, 0.400, 0.420, 0.440, 0.460, 0.480, 0.500, 0.520, 
                        0.540, 0.575, 0.625, 0.675, 0.725, 0.775, 0.825, 0.875, 0.925, 0.975, 
                        1.050, 1.150, 1.250, 1.350, 1.450, 1.550, 1.650, 1.750, 1.850, 1.950, 
                        2.050, 2.150, 2.250, 2.350, 2.450, 2.600, 2.800, 3.000, 3.200, 3.400, 
                        3.600, 3.800, 4.000, 4.200, 4.400, 4.600, 4.800, 5.000, 5.200, 5.400,
                        5.600, 5.800, 6.000, 6.200, 6.400, 6.600, 6.800, 7.000, 7.200, 7.400, 
                        7.750, 8.250, 8.750, 9.250, 9.750, 10.250, 10.750, 11.250, 11.750, 
                        12.250, 12.750, 13.250, 13.750, 14.250, 14.750, 15.500, 16.500, 17.500, 
                        18.500, 19.500, 20.500, 21.500, 22.500, 23.500, 24.500, 25.500, 26.500, 
                        27.500, 28.500, 29.500, 30.500, 31.500, 32.500, 33.500, 34.500, 35.500, 
                        36.500, 37.500, 38.500, 39.500, 40.500}; //MeV

	*/double binEnergies[] = {.6619,.6621};					
	// normalize input BinEnergy
    double NBinEnergy = medianBinEnergy; //MeV
    // get bin edge energies
	for (int i = 0; i < sizeof(binEnergies); i++) {
		if (binEnergies[i] > NBinEnergy) {
			binHigh = binEnergies[i];
			binLow = binEnergies[i - 1];
			break;
		}
	}
	
	// name for output file and some other stuff
	string outFileE = std::to_string(medianBinEnergy);
	outFileE = outFileE.substr(0, 5);
	string particleInputPrefix = outFileE + "MeV";
	cout << "The output prefix is: " << particleInputPrefix;
	/*
	string particleInputFilename = argv[1];
	// get particleInputFilename Prefix for name mangling 
	int start = 0;
	int stop = particleInputFilename.find_last_of('_');
	string particleInputPrefix = particleInputFilename.substr(start,stop);
	*/
	// construct the default run manager
	G4RunManager* runManager = new G4RunManager;

	// set mandatory initialization classes
	runManager->SetUserInitialization(new myDetectorConstruction(particleInputPrefix));
	myPhysicsList* phys = new myPhysicsList;
	runManager->SetUserInitialization(phys);	
	runManager->SetUserInitialization(new myActionInitialization(medianBinEnergy));	
	cout << "hold 1\n";

	//initialize G4 kernal
	//runManager->Initialize();

// get the pointer to the User Interface manager
   G4UImanager* UImanager = G4UImanager::GetUIpointer();

   if (argc>2)   // batch mode
   {
      G4String fileName = argv[2];
      G4String command = "/control/execute ";
      UImanager->ApplyCommand(command+fileName);
   }
   else
   {  // interactive mode : define UI session
//#ifdef G4VIS_USE
  G4VisManager* visManager = new G4VisExecutive;
  visManager->Initialize();
//#endif

//#ifdef G4UI_USE
     G4UIExecutive* ui = new G4UIExecutive(argc, argv);
     G4String command = "/control/execute vis.mac";
     UImanager->ApplyCommand(command);
     ui->SessionStart();
		 G4cout << "foobar" << G4endl;
     delete ui;
//#endif

//#ifdef G4VIS_USE
	delete visManager;
//#endif

	
   }
}
