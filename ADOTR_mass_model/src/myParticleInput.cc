#include "myParticleInput.hh"
#include "myParticle.hh"
#include "myRunAction.hh"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <math.h>
#include "Randomize.hh"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"

using namespace std;

extern double binHigh, binLow,medianBinEnergy;

myParticleInput::myParticleInput() //double BinEnergy
{
	// This part seeds the random number generator
  srand(1337); // I have seen examples use srand(time([int])), but I'm not sure if that's required yet
		
  return;
}

myParticleInput::~myParticleInput()
{
  delete[] fEvent;
  delete[] fParticle;
  delete[] fArrivalTime; 
  delete[] fEnergy;
  delete[] fPosX;
  delete[] fPosY;
  delete[] fPosZ;
  delete[] fDirX;
  delete[] fDirY;
  delete[] fDirZ;
  delete[] fECD;
  delete[] fWeight;
}

double * myParticleInput::generateParticleRands() 
{
    static double rands[3];
	// pick 3 random numbers between 0 and 1 then multiply it to the X and Y position and Bin energy
	// then add the 3 numbers to the fEnergy, fPosX, and fPosY
	// MAKE SURE THE SRAND() IS RUN
	
    rands[0] = binLow + ((double)rand() / RAND_MAX) * (binHigh - binLow);
    rands[1] = -0.5 + ((double)rand() / RAND_MAX);
    rands[2] = -0.5 + ((double)rand() / RAND_MAX);
    return rands;
}

myParticle myParticleInput::getParticle()
{
  // For each photon run:
  // 1.  Specify it's energy 
  // 2.  Specify it's direction
  // 3.  Specify it's location on an input sphere
 
  myParticle particle;
 
//set the energy
  double randE = binLow + ((double)rand() / RAND_MAX) * (binHigh - binLow); //Generates random energy between small energy bin 

  particle.set_Energy(randE);
  particle.set_ParticleDefinition("gamma"); 
  particle.set_ArrivalTime(0.0); 

// set the direction  
  double dir[3] = {0.0, 0.0, -1.0}; //hor*cos(phi), hor*sin(phi), zd
  //cout << "dir*dir " << dir[0]*dir[0] + dir[1]*dir[1] + dir[2]*dir[2] << endl;
  
  particle.set_StartDir(dir[0],dir[1],dir[2]); //
  //cout << "Direction " << dir[0] << " " << dir[1] << " " << dir[2] << G4endl;

// CHOOSE A STARTING POSITION randomly on the surface of a semi-sphere 

  double random_radius = G4UniformRand();
  double random_phi2 = G4UniformRand(); 
  double r = sqrt(random_radius);
  double phi2 = 2.0 * pi * random_phi2;
  double x = r * sin(phi2);
  double y = r * cos(phi2);
  double z = sqrt(1.0 - x*x - y*y); 

  particle.set_StartXYZ(x,y,z);
 
	return particle;
}
