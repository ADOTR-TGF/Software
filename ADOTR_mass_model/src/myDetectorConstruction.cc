#include "myDetectorConstruction.hh"
#include "myDetectorSD.hh"

#include "G4UserLimits.hh"
#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4Orb.hh"
#include "G4SubtractionSolid.hh"
#include "G4SystemOfUnits.hh"
#include "G4PVPlacement.hh"
#include "G4LogicalVolume.hh"
#include "G4VisAttributes.hh"
#include "G4PhysicalConstants.hh"

#include "G4SDManager.hh"
#include "G4GeometryManager.hh"
#include "G4VSensitiveDetector.hh"
#include "G4Material.hh"

#include "G4ios.hh"
#include <string>

void ConstructFloor(G4LogicalVolume*);

myDetectorConstruction::myDetectorConstruction(string particleInputPrefix)
: G4VUserDetectorConstruction(),
  fScoringVolume(0)
{ 

 fParticleInputPrefix = new string(particleInputPrefix);
 
}

myDetectorConstruction::~myDetectorConstruction()
{ 

}

G4VPhysicalVolume* myDetectorConstruction::Construct()
{

  G4bool checkOverlaps = true;
  
  // Get nist material manager
  //
  G4NistManager* nist = G4NistManager::Instance();

  // SetWorldMaximumExtent for scaling checkOverlap precision
  G4double pRmax = 1.5 * m;
  //G4double pDz = 3.0 * m;
  G4GeometryManager::GetInstance()->SetWorldMaximumExtent(pRmax);
  
  //
  // World
  //

  // Material
  G4Material* world_mat = nist->FindOrBuildMaterial("G4_Galactic");

  // Dimensions - Orb
  G4double world_pRmax = 1.1*pRmax;


  // Geometry - Orb
  G4Orb* solidWorld =
    new G4Orb("World",                 // its name 
               world_pRmax);           // its size


  G4LogicalVolume* logicWorld = 
    new G4LogicalVolume(solidWorld,    //its solid
                        world_mat,     //its material
                        "World");      //its name

  G4VPhysicalVolume* physWorld = 
    new G4PVPlacement(0,               //no rotation
                      G4ThreeVector(), //at (0,0,0)
                      logicWorld,      //its logical volume
                      "World",         //its name
                      0,               //its mother volume
                      false,           //no boolean operation
                      0,               //copy number
                      true);           //overlaps checking


  //
  // Envelope
  //

  G4Material *envelope_mat = nist->FindOrBuildMaterial("G4_AIR"); //SlabMat;
  G4cout << envelope_mat << G4endl;
 
  // Dimensions - Orb
  G4double envelope_pRmax = pRmax;


  // Geometry - Orb
  G4Orb* solidEnvelope =
    new G4Orb("Envelope",                 // its name 
               envelope_pRmax);            // its size


  G4LogicalVolume* logicEnvelope = 
    new G4LogicalVolume(solidEnvelope,    //its solid
                        envelope_mat,     //its material
                        "Envelope");      //its name

   new G4PVPlacement(0,                  //no rotation
                     G4ThreeVector(),    //at (0,0,0)
                     logicEnvelope,      //its logical volume
                     "Envelope",         //its name
                     logicWorld,         //its mother volume
                     false,              //no boolean operation
                     0,                  //copy number
                     true);              //overlaps checking

  // create inch unit
  static const G4double inch = 2.54*cm;
  
  // Material definitions of instrument components
  G4double z, a, density;
  G4String name, symbol;
  G4int ncomponents; 

  a = 12.02*g/mole;
  G4Element* elC = new G4Element(name="Carbon", symbol="C", z=6., a);

  a = 55.85*g/mole;
  G4Element* elFe  = new G4Element(name="Iron",symbol="Fe",z=26.,a);

  a  =  54.94*g/mole;
  G4Element* elMn   =  new G4Element("Manganese","Mn",z=25.,a);

  a = 28.09*g/mole;
  G4Element* elSi  = new G4Element("Silicon","Si",z=14.,a);

  
  density = 7.84*g/cm3 ;
  G4Material* steel = new G4Material(name="Steel",density,ncomponents=4);
  steel->AddElement(elMn, 0.0165);
  steel->AddElement(elSi, 0.01);
  steel->AddElement(elC, 0.005);
  steel->AddElement(elFe, 0.9685);
  
  G4Material *steel_mat = steel;
  
  G4Material *LgPl_mat 
    = nist->FindOrBuildMaterial("G4_PLASTIC_SC_VINYLTOLUENE");
  G4Material *NaI_mat 
    = nist->FindOrBuildMaterial("G4_SODIUM_IODIDE");
  G4Material *Al_mat 
    = nist->FindOrBuildMaterial("G4_Al");  
  G4Material *Air_mat 
    = nist->FindOrBuildMaterial("G4_AIR");
    
  // Dimensions of instrument components
  //Instrument box
  G4double box_hx = 24/2.0 * inch; 
  G4double box_hy = 24/2.0 * inch;
  G4double box_hz = 10/2.0 * inch; 
  G4double thick  = 0.0625 * inch;
  //inner plate
  G4double inner_plate_hx = 22/2.0 * inch;
  G4double inner_plate_hy = 22/2.0 * inch;
  G4double inner_plate_hz = .25/2.0 * inch;
  //outer plate
  G4double outer_plate_hx = 24/2.0 * inch;
  G4double outer_plate_hy = 24/2.0 * inch;
  G4double outer_plate_hz = .5/2.0 * inch;
  
  //GPS unit
  G4double gpsbox_hx = 4.3/2.0 * inch; 
  G4double gpsbox_hy = 2.31/2.0 * inch;
  G4double gpsbox_hz = 2.05/2.0 * inch; 
  G4double gpsthick  = 0.071 * inch;
  	 
  //large plastic detector housing
  G4double LgPl_housing_hx = 21/2.0 * inch; 
  G4double LgPl_housing_hy = 3/2.0 * inch;
  G4double LgPl_housing_hz = 3/2.0 * inch;
  //open space for LgPL PMT and electronics
  G4double LgPl_pmt_hx = 8.2/2.0 * inch; 
  G4double LgPl_pmt_hy = 2.5/2.0 * inch;
  G4double LgPl_pmt_hz = 2.5/2.0 * inch;
  // large plastic scintillator
  G4double LgPl_hx = 11.8/2.0 * inch; 
  G4double LgPl_hy = 2.5/2.0 * inch;
  G4double LgPl_hz = 2.5/2.0 * inch;

  // NaI detector housing
  G4double NaI_housing_pRmin = 0.0;
  G4double NaI_housing_pRmax = 1.25 * inch; // radius
  G4double NaI_housing_pDz =   8.5/2.0 * inch; // half length
  G4double NaI_housing_pSPhi = 0.0; 
  G4double NaI_housing_pDPhi = 2.0*pi;
  //open space for NaI PMT and electronics
  G4double NaI_pmt_pRmin = 0.0;
  G4double NaI_pmt_pRmax = 1.0 * inch; // radius
  G4double NaI_pmt_pDz =   3.0 * inch; // half length
  G4double NaI_pmt_pSPhi = 0.0; 
  G4double NaI_pmt_pDPhi = 2.0*pi;
  // NaI scintillator
  G4double NaI_pRmin = 0.0;
  G4double NaI_pRmax = 1.0 * inch; // radius
  G4double NaI_pDz =   1.0 * inch; // half length
  G4double NaI_pSPhi = 0.0; 
  G4double NaI_pDPhi = 2.0*pi;

  //positions and orientations instrument components
  G4RotationMatrix yRot90deg = G4RotationMatrix();
  yRot90deg.rotateY(90*deg);

  G4RotationMatrix noRot = G4RotationMatrix();
  noRot.rotateY(0);

  G4RotationMatrix yzRot90deg = G4RotationMatrix(); //new
  yzRot90deg.rotateY(90*deg);
  yzRot90deg.rotateZ(90*deg);

  G4RotationMatrix yyRot45deg = G4RotationMatrix(); //test
  yyRot45deg.rotateY(45*deg);
   
  G4ThreeVector LgPl_housing_position = G4ThreeVector(-1 * inch, -8.5 * inch, -1.825 * inch);
  G4Transform3D LgPl_housing_transform = G4Transform3D(noRot, LgPl_housing_position);
   
  G4ThreeVector LgPl_position = G4ThreeVector(-4.1 * inch, 0 * inch, 0 * inch); //with regard to housing
  G4Transform3D LgPl_transform = G4Transform3D(noRot, LgPl_position);
  
  G4ThreeVector LgPl_pmt_position = G4ThreeVector(5.9 * inch, 0 * inch, 0 * inch); //with regard to housing
  G4Transform3D LgPl_pmt_transform = G4Transform3D(noRot, LgPl_pmt_position);
  
  G4ThreeVector NaI_housing_position = G4ThreeVector(-3 * inch, -4 * inch, -2 * inch);
  G4Transform3D NaI_housing_transform = G4Transform3D(yRot90deg, NaI_housing_position);
  
  G4ThreeVector NaI_position = G4ThreeVector(0 * inch, 0 * inch, -3 * inch); //with regard to housing -3
  G4Transform3D NaI_transform = G4Transform3D(noRot, NaI_position);
  
  G4ThreeVector NaI_pmt_position = G4ThreeVector(0 * inch, 0 * inch, 1 * inch); //with regard to housing
  G4Transform3D NaI_pmt_transform = G4Transform3D(noRot, NaI_pmt_position);

  G4ThreeVector box_position = G4ThreeVector(0 * inch, 0 * inch, 0 * inch);
  G4Transform3D box_transform = G4Transform3D(noRot, box_position);
  
  G4ThreeVector inner_plate_position = G4ThreeVector(0 * inch, 0 * inch, -3.5 * inch);
  G4Transform3D inner_plate_transform = G4Transform3D(noRot, inner_plate_position);
 
  G4ThreeVector outer_plate_position = G4ThreeVector(0 * inch, 0 * inch, 5.3125 * inch);
  G4Transform3D outer_plate_transform = G4Transform3D(noRot, outer_plate_position);
  
  G4ThreeVector gpsbox_position = G4ThreeVector(6 * inch, -4.5* inch, -2.25 * inch);
  G4Transform3D gpsbox_transform = G4Transform3D(noRot, gpsbox_position);
  
  //
  // Defining logic volumes of instrument components
  //
  
  
  //
  // steel box
  //
  
  G4Box* Outer_Box
    = new G4Box("outer_Box",
                box_hx+thick,
                box_hy+thick,
                box_hz+thick);

  G4Box* Inner_Box
    = new G4Box("Inner_box",
                box_hx,
                box_hy,
                box_hz);
                
  G4SubtractionSolid *solidBox = 
		new G4SubtractionSolid("InstrumentBox", Outer_Box, Inner_Box);
                
  G4LogicalVolume* logicBox =
      new G4LogicalVolume(solidBox,   //its solid
                          steel_mat,    //its material
                          "Box");     //its name
                          
      new G4PVPlacement(box_transform,
                        logicBox,     //its logical volume
                        "Box",        // its name
                        logicEnvelope,  //its mother volume
                        false,          // no boolean operations
                        0,               // its copy number
                        checkOverlaps);  //check overlaps

  
  //
  // Inner steel plate 
  //
  
  G4Box* Inner_Plate
    = new G4Box("Inner_Plate",
                 inner_plate_hx,
                 inner_plate_hy,
                 inner_plate_hz);
    
  G4LogicalVolume* logicInner_Plate = 
      new G4LogicalVolume(Inner_Plate,   //its solid
                          steel_mat,    //its material
                          "Inner_Plate");     //its name
                          
      new G4PVPlacement(inner_plate_transform,
                        logicInner_Plate,     //its logical volume
                        "Inner_Plate",        // its name
                        logicEnvelope,  //its mother volume
                        false,          // no boolean operations
                        0,               // its copy number
                        checkOverlaps);  //check overlaps
   
   //
  // Outer steel plate 
  //
  
  G4Box* Outer_Plate
    = new G4Box("Outer_Plate",
                 outer_plate_hx,
                 outer_plate_hy,
                 outer_plate_hz);
    
  G4LogicalVolume* logicOuter_Plate = 
      new G4LogicalVolume(Outer_Plate,   //its solid
                          steel_mat,    //its material
                          "Outer_Plate");     //its name
                          
      new G4PVPlacement(outer_plate_transform,
                        logicOuter_Plate,     //its logical volume
                        "Outer_Plate",        // its name
                        logicEnvelope,  //its mother volume
                        false,          // no boolean operations
                        0,               // its copy number
                        checkOverlaps);  //check overlaps   
  
  //
  // GPS box
  //
  G4Box* outer_Box
    = new G4Box("Outer_Box",
                gpsbox_hx+gpsthick,
                gpsbox_hy+gpsthick,
                gpsbox_hz+gpsthick);

  G4Box* inner_Box
    = new G4Box("inner_box",
                gpsbox_hx,
                gpsbox_hy,
                gpsbox_hz);
                
  G4SubtractionSolid *solidBox_gps = 
		new G4SubtractionSolid("GPSBox", outer_Box, inner_Box);
                
  G4LogicalVolume* logicBox_gps =
      new G4LogicalVolume(solidBox_gps,   //its solid
                          Al_mat,    //its material
                          "GPSBox");     //its name
                          
      new G4PVPlacement(gpsbox_transform,
                        logicBox_gps,     //its logical volume
                        "GPSBox",        // its name
                        logicEnvelope,  //its mother volume
                        false,          // no boolean operations
                        0,               // its copy number
                        checkOverlaps);  //check overlaps

  
  
  
  //
  //  Large Plastic
  //
  G4Box* solidLgPl_housing
	= new G4Box("LgPl_housing",
				LgPl_housing_hx,
				LgPl_housing_hy,
				LgPl_housing_hz);

  G4LogicalVolume* logicLgPl_housing
    = new G4LogicalVolume(solidLgPl_housing,      //its solid
                          Al_mat,       //its material
                          "LgPl_housing");        //its name 

      new G4PVPlacement(LgPl_housing_transform, 
                        logicLgPl_housing,       //its logical volume
                        "LgPl_housing",           //its name
                        logicEnvelope,        //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap
  				
  G4Box* solidLgPl
	= new G4Box("LgPl",
				LgPl_hx,
				LgPl_hy,
				LgPl_hz);

  fLogicLgPl
    = new G4LogicalVolume(solidLgPl,      //its solid
                          LgPl_mat,       //its material
                          "LgPl");        //its name 

      new G4PVPlacement(LgPl_transform, 
                        fLogicLgPl,       //its logical volume
                        "LgPl",           //its name
                        logicLgPl_housing, //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap
                        
  G4Box* solidLgPl_pmt
	= new G4Box("LgPl_pmt",
				LgPl_pmt_hx,
				LgPl_pmt_hy,
				LgPl_pmt_hz);

  G4LogicalVolume* logicLgPl_pmt
    = new G4LogicalVolume(solidLgPl_pmt,      //its solid
                          Air_mat,       //its material
                          "LgPl_pmt");        //its name 

      new G4PVPlacement(LgPl_pmt_transform, 
                        logicLgPl_pmt,       //its logical volume
                        "LgPl_pmt",           //its name
                        logicLgPl_housing, //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap

  //
  //  NaI
  //
  
  G4Tubs* solidNaI_housing
    = new G4Tubs("NaI_housing",                   //its name
                NaI_housing_pRmin,              //its size 
                NaI_housing_pRmax,
                NaI_housing_pDz,
                NaI_housing_pSPhi,
                NaI_housing_pDPhi);

  G4LogicalVolume* logicNaI_housing
    = new G4LogicalVolume(solidNaI_housing,       //its solid
                          Al_mat,        //its material
                          "NaI_housing");         //its name 

      new G4PVPlacement(NaI_housing_transform, 
                        logicNaI_housing,        //its logical volume
                        "NaI_housing",            //its name
                        logicEnvelope,        //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap
  
  G4Tubs* solidNaI
    = new G4Tubs("NaI",                   //its name
                NaI_pRmin,              //its size 
                NaI_pRmax,
                NaI_pDz,
                NaI_pSPhi,
                NaI_pDPhi);

  //G4LogicalVolume* logicNaI
  fLogicNaI
    = new G4LogicalVolume(solidNaI,       //its solid
                          NaI_mat,        //its material
                          "NaI");         //its name 

      new G4PVPlacement(NaI_transform, 
                        fLogicNaI,        //its logical volume
                        "NaI",            //its name
                        logicNaI_housing,        //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap

  G4Tubs* solidNaI_pmt
    = new G4Tubs("NaI_pmt",                   //its name
                NaI_pmt_pRmin,              //its size 
                NaI_pmt_pRmax,
                NaI_pmt_pDz,
                NaI_pmt_pSPhi,
                NaI_pmt_pDPhi);

  G4LogicalVolume* logicNaI_pmt
    = new G4LogicalVolume(solidNaI_pmt,       //its solid
                          Air_mat,        //its material
                          "NaI_pmt");         //its name 

      new G4PVPlacement(NaI_pmt_transform, 
                        logicNaI_pmt,        //its logical volume
                        "NaI_pmt",            //its name
                        logicNaI_housing,        //its mother (logical) volume
                        false,            //no boolean operations
                        0,                //its copy number 
                        checkOverlaps);   //checkOverlap

    //constructing additional volumes, i.e. floors, aircraft fuselage etc.. 
	//floor
	//ConstructFloor(logicEnvelope);


  //
  // Visualization
  //
  //logicWorld->  SetVisAttributes(new G4VisAttributes(G4Colour(0.,1.,1.))); //unknown
  logicEnvelope->SetVisAttributes(new G4VisAttributes(G4Colour(0.,0.,1.))); //giant blue sphere 
  logicWorld->  SetVisAttributes(G4VisAttributes::GetInvisible()); // unknown
  logicEnvelope->  SetVisAttributes(G4VisAttributes::GetInvisible());
  logicLgPl_housing-> SetVisAttributes(new G4VisAttributes(G4Colour(1.,0.,0.))); //red
  logicLgPl_pmt-> SetVisAttributes(new G4VisAttributes(G4Colour(0.,0.,1.))); //blue
  fLogicLgPl->  SetVisAttributes(new G4VisAttributes(G4Colour(1.,1.,0.))); //yellow
  logicNaI_housing-> SetVisAttributes(new G4VisAttributes(G4Colour(1.,0.,0.))); //red
  logicNaI_pmt-> SetVisAttributes(new G4VisAttributes(G4Colour(0.,0.,1.))); //blue
  fLogicNaI->   SetVisAttributes(new G4VisAttributes(G4Colour(1.,1.,0.)));  //yellow
  logicBox_gps-> SetVisAttributes(new G4VisAttributes(G4Colour(1.,0.,0.))); //red

  
  
  return physWorld;

}

//  Define the detector volumes as sensitive detectors 
void myDetectorConstruction::ConstructSDandField()
{
  
  G4SDManager* SDman = G4SDManager::GetSDMpointer();
  char SDName[50];

  sprintf(SDName, "LgPl_%s", fParticleInputPrefix->c_str());
  G4VSensitiveDetector* LgPl 
    = new myDetectorSD(SDName, "LgPlHitsCollection");
  SDman->AddNewDetector(LgPl);
  fLogicLgPl->SetSensitiveDetector(LgPl);

  sprintf(SDName, "NaI_%s", fParticleInputPrefix->c_str());
  G4VSensitiveDetector* NaI 
    = new myDetectorSD(SDName, "NaIHitsCollection");
  SDman->AddNewDetector(NaI);
  fLogicNaI->SetSensitiveDetector(NaI);
}

//defining a floor volume 
void ConstructFloor(G4LogicalVolume *logicEnvelope){
	
	//check line 414
	//this is the ground
  G4NistManager* nist = G4NistManager::Instance();
  static const G4double inch = 2.54*cm;
  bool checkOverlaps = true;
  
	//material - glass (silicon dioxide); density 4.5 g/cm3 subject to change
	G4Material* floor_mat = 
    nist->FindOrBuildMaterial("G4_CONCRETE"); //"G4_SILICON_DIOXIDE"
	G4cout << floor_mat << G4endl;
	
	// Dimensions
	G4double floor_hx = 160.0/2.0 * inch; //subject ti change
	G4double floor_hy = 160.0/2.0 * inch;
	G4double floor_hz = 70.0/2.0 * inch;

	// Geometry
	G4Box *floor = 
		new G4Box("solidFloor", 
							floor_hx/2.0, 
							floor_hy/2.0, 
							floor_hz/2.0);

  G4LogicalVolume* logicFloor = 
    new G4LogicalVolume(floor,   //its solid
                        floor_mat,    //its material
                        "Floor");     //its name

    new G4PVPlacement(0,               //no rotation
                      G4ThreeVector(0,0,-(((floor_hz)/2.0)+(12.5/2.0  * inch))), //it's position
                      logicFloor,    //its logical volume
                      "Floor",       //its name
                      logicEnvelope,   //its mother volume
                      false,           //no boolean operation
                      0,               //copy number
                      checkOverlaps);  //overlaps checking
  
  logicFloor-> 	SetVisAttributes(new G4VisAttributes(G4Colour(0.,1.,0.))); //floor

}

