#include "myDetectorConstruction.hh"
#include "myDetectorSD.hh"

#include "G4UserLimits.hh"
#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
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

myDetectorConstruction::myDetectorConstruction(string inputPrefix)
: G4VUserDetectorConstruction(),
  fScoringVolume(0), fLogicSD(0)
{ 

	fInputPrefix = new string(inputPrefix);

 
//########## begin output of Atmospheric_Standard_Slabs.py

// specify number of slabs in atmosphere
fnSlabs = 200; //100 meter thick slabs to 20km altitude

// slab altitudes at half-height
G4double slabs_z[] = 
{50*m, 150*m, 250*m, 350*m, 450*m, 550*m, 650*m, 750*m, 850*m, 950*m, 1050*m, 1150*m, 1250*m, 1350*m, 1450*m, 1550*m, 1650*m, 1750*m, 1850*m, 1950*m, 2050*m, 2150*m, 2250*m, 2350*m, 2450*m, 2550*m, 2650*m, 2750*m, 2850*m, 2950*m, 3050*m, 3150*m, 3250*m, 3350*m, 3450*m, 3550*m, 3650*m, 3750*m, 3850*m, 3950*m, 4050*m, 4150*m, 4250*m, 4350*m, 4450*m, 4550*m, 4650*m, 4750*m, 4850*m, 4950*m, 5050*m, 5150*m, 5250*m, 5350*m, 5450*m, 5550*m, 5650*m, 5750*m, 5850*m, 5950*m, 6050*m, 6150*m, 6250*m, 6350*m, 6450*m, 6550*m, 6650*m, 6750*m, 6850*m, 6950*m, 7050*m, 7150*m, 7250*m, 7350*m, 7450*m, 7550*m, 7650*m, 7750*m, 7850*m, 7950*m, 8050*m, 8150*m, 8250*m, 8350*m, 8450*m, 8550*m, 8650*m, 8750*m, 8850*m, 8950*m, 9050*m, 9150*m, 9250*m, 9350*m, 9450*m, 9550*m, 9650*m, 9750*m, 9850*m, 9950*m, 10050*m, 10150*m, 10250*m, 10350*m, 10450*m, 10550*m, 10650*m, 10750*m, 10850*m, 10950*m, 11050*m, 11150*m, 11250*m, 11350*m, 11450*m, 11550*m, 11650*m, 11750*m, 11850*m, 11950*m, 12050*m, 12150*m, 12250*m, 12350*m, 12450*m, 12550*m, 12650*m, 12750*m, 12850*m, 12950*m, 13050*m, 13150*m, 13250*m, 13350*m, 13450*m, 13550*m, 13650*m, 13750*m, 13850*m, 13950*m, 14050*m, 14150*m, 14250*m, 14350*m, 14450*m, 14550*m, 14650*m, 14750*m, 14850*m, 14950*m, 15050*m, 15150*m, 15250*m, 15350*m, 15450*m, 15550*m, 15650*m, 15750*m, 15850*m, 15950*m, 16050*m, 16150*m, 16250*m, 16350*m, 16450*m, 16550*m, 16650*m, 16750*m, 16850*m, 16950*m, 17050*m, 17150*m, 17250*m, 17350*m, 17450*m, 17550*m, 17650*m, 17750*m, 17850*m, 17950*m, 18050*m, 18150*m, 18250*m, 18350*m, 18450*m, 18550*m, 18650*m, 18750*m, 18850*m, 18950*m, 19050*m, 19150*m, 19250*m, 19350*m, 19450*m, 19550*m, 19650*m, 19750*m, 19850*m, 19950*m};

// slab half-heights
G4double slabs_pDz[] = 
{50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m, 50.0*m};

// slab densities
G4double slabs_rho[] = 
{1.219134377567*kg/m3, 1.207460504583*kg/m3, 1.195872704598*kg/m3, 1.184370532589*kg/m3, 1.172953544859*kg/m3, 1.161621299035*kg/m3, 1.150373354069*kg/m3, 1.139209270234*kg/m3, 1.128128609125*kg/m3, 1.117130933658*kg/m3, 1.106215808065*kg/m3, 1.0953827979*kg/m3, 1.084631470032*kg/m3, 1.073961392644*kg/m3, 1.063372135237*kg/m3, 1.052863268623*kg/m3, 1.042434364927*kg/m3, 1.032084997585*kg/m3, 1.021814741343*kg/m3, 1.011623172256*kg/m3, 1.001509867687*kg/m3, 0.991474406306*kg/m3, 0.981516368086*kg/m3, 0.971635334309*kg/m3, 0.961830887555*kg/m3, 0.952102611709*kg/m3, 0.942450091957*kg/m3, 0.932872914783*kg/m3, 0.923370667973*kg/m3, 0.913942940605*kg/m3, 0.90458932306*kg/m3, 0.895309407008*kg/m3, 0.886102785417*kg/m3, 0.876969052547*kg/m3, 0.867907803949*kg/m3, 0.858918636465*kg/m3, 0.850001148227*kg/m3, 0.841154938654*kg/m3, 0.832379608453*kg/m3, 0.823674759617*kg/m3, 0.815039995424*kg/m3, 0.806474920435*kg/m3, 0.797979140495*kg/m3, 0.789552262728*kg/m3, 0.78119389554*kg/m3, 0.772903648615*kg/m3, 0.764681132916*kg/m3, 0.756525960682*kg/m3, 0.748437745428*kg/m3, 0.740416101942*kg/m3, 0.732460646288*kg/m3, 0.724570995798*kg/m3, 0.716746769079*kg/m3, 0.708987586005*kg/m3, 0.701293067721*kg/m3, 0.693662836636*kg/m3, 0.686096516429*kg/m3, 0.67859373204*kg/m3, 0.671154109677*kg/m3, 0.663777276808*kg/m3, 0.656462862164*kg/m3, 0.649210495734*kg/m3, 0.642019808769*kg/m3, 0.634890433776*kg/m3, 0.627822004521*kg/m3, 0.620814156023*kg/m3, 0.613866524557*kg/m3, 0.606978747651*kg/m3, 0.600150464085*kg/m3, 0.59338131389*kg/m3, 0.586670938347*kg/m3, 0.580018979985*kg/m3, 0.57342508258*kg/m3, 0.566888891155*kg/m3, 0.560410051978*kg/m3, 0.55398821256*kg/m3, 0.547623021655*kg/m3, 0.541314129259*kg/m3, 0.535061186606*kg/m3, 0.528863846172*kg/m3, 0.522721761669*kg/m3, 0.516634588046*kg/m3, 0.510601981488*kg/m3, 0.504623599411*kg/m3, 0.49869910047*kg/m3, 0.492828144545*kg/m3, 0.487010392752*kg/m3, 0.481245507434*kg/m3, 0.475533152162*kg/m3, 0.469872991734*kg/m3, 0.464264692175*kg/m3, 0.458707920733*kg/m3, 0.453202345881*kg/m3, 0.447747637312*kg/m3, 0.442343465941*kg/m3, 0.436989503904*kg/m3, 0.431685424553*kg/m3, 0.426430902459*kg/m3, 0.421225613408*kg/m3, 0.416069234402*kg/m3, 0.410961443655*kg/m3, 0.405901920595*kg/m3, 0.400890345859*kg/m3, 0.395926401297*kg/m3, 0.391009769964*kg/m3, 0.386140136126*kg/m3, 0.381317185253*kg/m3, 0.376540604021*kg/m3, 0.371810080308*kg/m3, 0.367125303197*kg/m3, 0.362150785636*kg/m3, 0.356504392769*kg/m3, 0.350946206996*kg/m3, 0.345474847666*kg/m3, 0.34008895578*kg/m3, 0.334787193651*kg/m3, 0.32956824457*kg/m3, 0.324430812475*kg/m3, 0.319373621628*kg/m3, 0.314395416296*kg/m3, 0.309494960435*kg/m3, 0.304671037382*kg/m3, 0.299922449549*kg/m3, 0.295248018126*kg/m3, 0.290646582783*kg/m3, 0.286117001382*kg/m3, 0.28165814969*kg/m3, 0.277268921099*kg/m3, 0.272948226347*kg/m3, 0.268694993248*kg/m3, 0.264508166421*kg/m3, 0.26038670703*kg/m3, 0.256329592521*kg/m3, 0.252335816365*kg/m3, 0.248404387813*kg/m3, 0.244534331639*kg/m3, 0.240724687903*kg/m3, 0.236974511711*kg/m3, 0.233282872973*kg/m3, 0.229648856177*kg/m3, 0.226071560155*kg/m3, 0.222550097863*kg/m3, 0.219083596153*kg/m3, 0.215671195561*kg/m3, 0.212312050088*kg/m3, 0.209005326991*kg/m3, 0.205750206572*kg/m3, 0.202545881976*kg/m3, 0.199391558991*kg/m3, 0.196286455842*kg/m3, 0.193229803007*kg/m3, 0.190220843012*kg/m3, 0.187258830254*kg/m3, 0.184343030805*kg/m3, 0.181472722236*kg/m3, 0.178647193432*kg/m3, 0.175865744415*kg/m3, 0.173127686172*kg/m3, 0.170432340479*kg/m3, 0.167779039735*kg/m3, 0.165167126795*kg/m3, 0.162595954801*kg/m3, 0.16006488703*kg/m3, 0.157573296726*kg/m3, 0.155120566947*kg/m3, 0.152706090412*kg/m3, 0.15032926935*kg/m3, 0.147989515348*kg/m3, 0.145686249205*kg/m3, 0.143418900789*kg/m3, 0.141186908893*kg/m3, 0.138989721098*kg/m3, 0.136826793631*kg/m3, 0.134697591231*kg/m3, 0.132601587018*kg/m3, 0.130538262357*kg/m3, 0.128507106734*kg/m3, 0.126507617622*kg/m3, 0.124539300362*kg/m3, 0.122601668038*kg/m3, 0.120694241352*kg/m3, 0.118816548508*kg/m3, 0.116968125096*kg/m3, 0.11514851397*kg/m3, 0.113357265141*kg/m3, 0.111593935659*kg/m3, 0.109858089508*kg/m3, 0.108149297492*kg/m3, 0.106467137133*kg/m3, 0.104811192561*kg/m3, 0.103181054414*kg/m3, 0.101576319735*kg/m3, 0.099996591871*kg/m3, 0.098441480374*kg/m3, 0.096910600904*kg/m3, 0.095403575135*kg/m3, 0.093920030659*kg/m3, 0.09245960089*kg/m3, 0.091021924982*kg/m3, 0.089606647728*kg/m3};

// slab pressures
G4double slabs_P[] = 
{ 100725.787642*pascal, 99535.998082*pascal, 98357.650989*pascal, 97190.661464*pascal, 96034.945052*pascal, 94890.417739*pascal, 93756.995953*pascal, 92634.596562*pascal, 91523.136871*pascal, 90422.534622*pascal, 89332.707995*pascal, 88253.575601*pascal, 87185.056485*pascal, 86127.070125*pascal, 85079.536426*pascal, 84042.375727*pascal, 83015.508788*pascal, 81998.856801*pascal, 80992.341379*pascal, 79995.88456*pascal, 79009.408804*pascal, 78032.836992*pascal, 77066.092425*pascal, 76109.09882*pascal, 75161.780314*pascal, 74224.061456*pascal, 73295.867213*pascal, 72377.122961*pascal, 71467.754491*pascal, 70567.688002*pascal, 69676.850101*pascal, 68795.167807*pascal, 67922.56854*pascal, 67058.980128*pascal, 66204.330801*pascal, 65358.549193*pascal, 64521.564339*pascal, 63693.305671*pascal, 62873.703022*pascal, 62062.68662*pascal, 61260.187092*pascal, 60466.135456*pascal, 59680.463125*pascal, 58903.101903*pascal, 58133.983984*pascal, 57373.041953*pascal, 56620.208782*pascal, 55875.41783*pascal, 55138.602839*pascal, 54409.697939*pascal, 53688.637639*pascal, 52975.356832*pascal, 52269.79079*pascal, 51571.875164*pascal, 50881.545983*pascal, 50198.739651*pascal, 49523.392948*pascal, 48855.443028*pascal, 48194.827417*pascal, 47541.484011*pascal, 46895.351079*pascal, 46256.367255*pascal, 45624.471542*pascal, 44999.603309*pascal, 44381.70229*pascal, 43770.708581*pascal, 43166.562642*pascal, 42569.205293*pascal, 41978.577713*pascal, 41394.621442*pascal, 40817.278373*pascal, 40246.490758*pascal, 39682.201203*pascal, 39124.352666*pascal, 38572.88846*pascal, 38027.752244*pascal, 37488.888032*pascal, 36956.240182*pascal, 36429.753401*pascal, 35909.372741*pascal, 35395.0436*pascal, 34886.711716*pascal, 34384.323173*pascal, 33887.824394*pascal, 33397.162139*pascal, 32912.283511*pascal, 32433.135947*pascal, 31959.66722*pascal, 31491.825437*pascal, 31029.559041*pascal, 30572.816803*pascal, 30121.547829*pascal, 29675.701551*pascal, 29235.227732*pascal, 28800.07646*pascal, 28370.19815*pascal, 27945.543541*pascal, 27526.063696*pascal, 27111.71*pascal, 26702.434159*pascal, 26298.188198*pascal, 25898.924461*pascal, 25504.59561*pascal, 25115.154621*pascal, 24730.554787*pascal, 24350.749713*pascal, 23975.693317*pascal, 23605.339828*pascal, 23239.643787*pascal, 22878.560039*pascal, 22522.090651*pascal, 22170.942518*pascal, 21825.279969*pascal, 21485.01714*pascal, 21150.069516*pascal, 20820.353905*pascal, 20495.788423*pascal, 20176.292468*pascal, 19861.7867*pascal, 19552.193028*pascal, 19247.43458*pascal, 18947.435694*pascal, 18652.121892*pascal, 18361.419863*pascal, 18075.257446*pascal, 17793.563613*pascal, 17516.268448*pascal, 17243.30313*pascal, 16974.599919*pascal, 16710.092136*pascal, 16449.714147*pascal, 16193.401347*pascal, 15941.090143*pascal, 15692.71794*pascal, 15448.223122*pascal, 15207.545041*pascal, 14970.623999*pascal, 14737.401233*pascal, 14507.818899*pascal, 14281.820064*pascal, 14059.348684*pascal, 13840.349592*pascal, 13624.76849*pascal, 13412.551925*pascal, 13203.647287*pascal, 12998.002787*pascal, 12795.567447*pascal, 12596.291091*pascal, 12400.124326*pascal, 12207.018533*pascal, 12016.925856*pascal, 11829.799188*pascal, 11645.59216*pascal, 11464.25913*pascal, 11285.755169*pascal, 11110.036053*pascal, 10937.058251*pascal, 10766.778913*pascal, 10599.155861*pascal, 10434.147576*pascal, 10271.713192*pascal, 10111.812479*pascal, 9954.40584*pascal, 9799.454298*pascal, 9646.919485*pascal, 9496.763634*pascal, 9348.94957*pascal, 9203.4407*pascal, 9060.201003*pascal, 8919.195022*pascal, 8780.387857*pascal, 8643.745153*pascal, 8509.233092*pascal, 8376.818387*pascal, 8246.468271*pascal, 8118.150491*pascal, 7991.833297*pascal, 7867.485437*pascal, 7745.076149*pascal, 7624.575152*pascal, 7505.952638*pascal, 7389.179266*pascal, 7274.226154*pascal, 7161.064873*pascal, 7049.667439*pascal, 6940.006303*pascal, 6832.054351*pascal, 6725.78489*pascal, 6621.171647*pascal, 6518.188759*pascal, 6416.810768*pascal, 6317.012614*pascal, 6218.769629*pascal, 6122.057532*pascal, 6026.852419*pascal, 5933.130764*pascal, 5840.869407*pascal, 5750.045548*pascal, 5660.636748*pascal, 5572.620917*pascal };

// slab temperatures
G4double slabs_T[] = 
{ 287.825*kelvin, 287.175*kelvin, 286.525*kelvin, 285.875*kelvin, 285.225*kelvin, 284.575*kelvin, 283.925*kelvin, 283.276*kelvin, 282.626*kelvin, 281.976*kelvin, 281.326*kelvin, 280.676*kelvin, 280.027*kelvin, 279.377*kelvin, 278.727*kelvin, 278.077*kelvin, 277.428*kelvin, 276.778*kelvin, 276.128*kelvin, 275.479*kelvin, 274.829*kelvin, 274.18*kelvin, 273.53*kelvin, 272.881*kelvin, 272.231*kelvin, 271.582*kelvin, 270.932*kelvin, 270.283*kelvin, 269.633*kelvin, 268.984*kelvin, 268.334*kelvin, 267.685*kelvin, 267.036*kelvin, 266.386*kelvin, 265.737*kelvin, 265.088*kelvin, 264.439*kelvin, 263.789*kelvin, 263.14*kelvin, 262.491*kelvin, 261.842*kelvin, 261.193*kelvin, 260.543*kelvin, 259.894*kelvin, 259.245*kelvin, 258.596*kelvin, 257.947*kelvin, 257.298*kelvin, 256.649*kelvin, 256.0*kelvin, 255.351*kelvin, 254.702*kelvin, 254.053*kelvin, 253.404*kelvin, 252.755*kelvin, 252.106*kelvin, 251.458*kelvin, 250.809*kelvin, 250.16*kelvin, 249.511*kelvin, 248.862*kelvin, 248.214*kelvin, 247.565*kelvin, 246.916*kelvin, 246.267*kelvin, 245.619*kelvin, 244.97*kelvin, 244.321*kelvin, 243.673*kelvin, 243.024*kelvin, 242.376*kelvin, 241.727*kelvin, 241.079*kelvin, 240.43*kelvin, 239.781*kelvin, 239.133*kelvin, 238.485*kelvin, 237.836*kelvin, 237.188*kelvin, 236.539*kelvin, 235.891*kelvin, 235.243*kelvin, 234.594*kelvin, 233.946*kelvin, 233.298*kelvin, 232.649*kelvin, 232.001*kelvin, 231.353*kelvin, 230.705*kelvin, 230.057*kelvin, 229.408*kelvin, 228.76*kelvin, 228.112*kelvin, 227.464*kelvin, 226.816*kelvin, 226.168*kelvin, 225.52*kelvin, 224.872*kelvin, 224.224*kelvin, 223.576*kelvin, 222.928*kelvin, 222.28*kelvin, 221.632*kelvin, 220.984*kelvin, 220.336*kelvin, 219.688*kelvin, 219.04*kelvin, 218.393*kelvin, 217.745*kelvin, 217.097*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin, 216.65*kelvin };


 //########## end output of Atmospheric_Standard_Slabs.py

	fLogicSlabSDs = static_cast<G4LogicalVolume*>(::operator new(sizeof(G4LogicalVolume)*fnSlabs));
	fStepLimits = static_cast<G4UserLimits*>(::operator new(sizeof(G4UserLimits)*fnSlabs));

	// initialize persistent arrays	
	fslabs_z = new double[fnSlabs];
	std::memcpy(fslabs_z, slabs_z, sizeof(slabs_z));
	fslabs_pDz = new double[fnSlabs];
	std::memcpy(fslabs_pDz, slabs_pDz, sizeof(slabs_pDz));
	fslabs_rho = new double[fnSlabs];
	std::memcpy(fslabs_rho, slabs_rho, sizeof(slabs_rho));
	fslabs_T = new double[fnSlabs];
	std::memcpy(fslabs_T, slabs_T, sizeof(slabs_T));
	fslabs_P = new double[fnSlabs];
	std::memcpy(fslabs_P, slabs_P, sizeof(slabs_P));
}

myDetectorConstruction::~myDetectorConstruction()
{ 
	// destruct fLogicSlabSDs array
	for(int i = fnSlabs-1; i >=0; --i){
		fLogicSlabSDs[i].~G4LogicalVolume();
	} 
	::operator delete[]( fLogicSlabSDs);

	// destruct fStepLimits array
	for(int i = fnSlabs-1; i >=0; --i){
		fStepLimits[i].~G4UserLimits();
	} 
	::operator delete[]( fStepLimits);

	delete[] fslabs_z;
	delete[] fslabs_pDz;
	delete[] fslabs_rho;
	delete[] fslabs_T;
	delete[] fslabs_P;
}

G4VPhysicalVolume* myDetectorConstruction::Construct()
{
  // Get nist material manager
  //
  G4NistManager* nist = G4NistManager::Instance();

  //
  // World
  //
 
	G4double pRmax = 20.0*km;
	G4double pDz   = 20.0*km; // half-length

	G4GeometryManager::GetInstance()->SetWorldMaximumExtent(2*pRmax);

  // TUBS
	G4double world_pRmin = 0.0;
	G4double world_pRmax = 1.2*pRmax;
	G4double world_pDz =   1.2*pDz; // half-length
	G4double world_pSPhi = 0.0; 
	G4double world_pDPhi = 2.0*pi;
  
  G4Material* world_mat = nist->FindOrBuildMaterial("G4_Galactic");

  // TUBS
  G4Tubs* solidWorld =
    new G4Tubs("World",                 // its name 
               world_pRmin,             // its size
               world_pRmax,
               world_pDz,
               world_pSPhi,
               world_pDPhi);

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
                      false);           //overlaps checking

  //
  // Envelope
  //
 
  // TUBS
	G4double envelope_pRmin = 0.0;
	G4double envelope_pRmax = 1.1*pRmax;
	G4double envelope_pDz =   1.1*pDz; // half-length
	G4double envelope_pSPhi = 0.0; 
	G4double envelope_pDPhi = 2.0*pi;
  
  G4Material* envelope_mat = nist->FindOrBuildMaterial("G4_Galactic");

  // TUBS
  G4Tubs* solidEnvelope =
    new G4Tubs("Envelope",                 // its name 
               envelope_pRmin,             // its size
               envelope_pRmax,
               envelope_pDz,
               envelope_pSPhi,
               envelope_pDPhi);

  G4LogicalVolume* logicEnvelope = 
    new G4LogicalVolume(solidEnvelope,    //its solid
                        envelope_mat,     //its material
                        "Envelope");      //its name

  //G4VPhysicalVolume* physEnvelope = 
    new G4PVPlacement(0,                  //no rotation
                      G4ThreeVector(),    //at (0,0,0)
                      logicEnvelope,      //its logical volume
                      "Envelope",         //its name
                      logicWorld,         //its mother volume
                      false,              //no boolean operation
                      0,                  //copy number
                      false);              //overlaps checking

	// Thermal Hydrogen in Water
	// N.B. Contribution of O from H2O is negligible compared to O2 in air
  fTS_H = new G4Element("TS_H_of_Water" ,"H" , 1., 1.0079*g/mole);
	//G4cout << fTS_H << G4endl;

  //
  // Atmosphere
  //
	for(G4int i=0; i<fnSlabs; i++)
		ConstructSlab(i,&logicEnvelope);

	

  //
  // Ocean or ground
  //

	// TUBS
	G4double ground_pRmin = 0.0;
	G4double ground_pRmax = pRmax;
	G4double ground_pDz =   500*m; // half-length
	G4double ground_pSPhi = 0.0; 
	G4double ground_pDPhi = 2.0*pi;

	G4double ground_z = -ground_pDz;

	// Material
  G4Material* ground_mat = nist->FindOrBuildMaterial("G4_WATER");
	//G4cout << ground_mat << G4endl;

  // position and orientation
  G4RotationMatrix yRot90deg = G4RotationMatrix();
  yRot90deg.rotateY(0*deg);

  G4ThreeVector ground_position = G4ThreeVector(0,0,ground_z);
  G4Transform3D ground_transform = G4Transform3D(yRot90deg, ground_position);

  G4Tubs* solidGround
    = new G4Tubs("Ground",              //its name
                ground_pRmin,           //its size 
                ground_pRmax,
                ground_pDz,
                ground_pSPhi,
                ground_pDPhi);
		
  G4LogicalVolume* logicGround = 
    new G4LogicalVolume(solidGround,    //its solid
                        ground_mat,     //its material
                        "Ground");      //its name

  new G4PVPlacement(ground_transform, 
            				logicGround,  			//its logical volume
            				"Ground",     			//its name
            				logicEnvelope,  	  //its mother (logical) volume
            				false,        			//no boolean operations
            				0,            			//its copy number 
            				false);        			//checkOverlap

  

  //
  // Visualization
  //
  logicWorld->SetVisAttributes(new G4VisAttributes(G4Colour(0.,1.,1.)));  
  logicGround->SetVisAttributes(new G4VisAttributes(G4Colour(0.5, 0.5, 0.5)));  
	logicWorld->SetVisAttributes(G4VisAttributes::GetInvisible());
	logicEnvelope->SetVisAttributes(G4VisAttributes::GetInvisible());


	return physWorld;

}

void myDetectorConstruction::ConstructSlab(G4int slabNo, 
	G4LogicalVolume** logicWorld)
{
	// make slab name
	char slabName[50]; 
	sprintf(slabName, "Slab%02i", slabNo);

	G4double slab_pRmin = 0.0;
	G4double slab_pRmax = 20*km; // radius
	G4double slab_pDz =   fslabs_pDz[slabNo]; // half length
	G4double slab_pSPhi = 0.0; 
	G4double slab_pDPhi = 2.0*pi;
	G4double slab_z = fslabs_z[slabNo]; 

	char slabInfo[256]; 
	sprintf(slabInfo, "Slab%02i Geometry: slab_pRmax=%g m, slab_z=%g m, slab_pDz=%g m\n", slabNo, slab_pRmax/m, slab_z/m, slab_pDz/m);
	//G4cout << slabInfo << G4endl;

  // detector positions and orientations
  G4RotationMatrix yRot90deg = G4RotationMatrix();
  yRot90deg.rotateY(0*deg);

  G4ThreeVector slab_position = G4ThreeVector(0,0,slab_z);
  G4Transform3D slab_transform = G4Transform3D(yRot90deg, slab_position);

	// Material Definitions 
	
	// Slab Air
	char materialName[50]; 
	sprintf(materialName, "Air%02i", slabNo);

	G4double density;
  G4double temperature;
  G4double pressure;
  G4NistManager* nist = G4NistManager::Instance();
	nist->SetVerbose(1);

	density = fslabs_rho[slabNo];
	temperature = fslabs_T[slabNo];
	pressure = fslabs_P[slabNo];

	G4Material *Air = nist->ConstructNewGasMaterial(materialName, "G4_AIR", temperature, pressure);

	// Slab Material - Mixture of Air and Rain 
	sprintf(materialName, "SlabMat%02i", slabNo);
	// http://www.wolframalpha.com/input/?i=1g%2Fcm%5E3*1inch%2F+(1m%2Fs*1hour)+to+mg%2Fcm%5E3
	// assume 1mm droplet size -> terminal velocity of 1m/s and 1 inch of rainfall per hour
	G4double rho_TS_H = 7.056e-3 * 2.0/18.0; // mg/cm3
	//G4double rho_TS_H = 0;
	G4double rho_air = density/(mg/cm3); 
	G4double fraction_Air = rho_air/(rho_air + rho_TS_H);
	G4double fraction_TS_H = rho_TS_H/(rho_air + rho_TS_H);
	G4Material* SlabMat = new G4Material(materialName, density, 2, kStateGas, temperature, pressure);  
  SlabMat->AddMaterial(Air, fraction_Air);
  SlabMat->AddElement(fTS_H, fraction_TS_H);

	//SlabMat = Air;

	//G4cout << SlabMat << G4endl; // output material properties
	//G4cout << "\t\t\t\t\tElmMassFraction of TS_H_of_Water: " << fraction_TS_H / perCent << "%" << G4endl << G4endl;
		
  G4Tubs* solidSlab
    = new G4Tubs(slabName,                 //its name
                slab_pRmin,                //its size 
                slab_pRmax,
                slab_pDz,
                slab_pSPhi,
                slab_pDPhi);

	new (fLogicSlabSDs+slabNo) G4LogicalVolume(solidSlab, SlabMat, slabName);
	
  new G4PVPlacement(slab_transform, 
                    (fLogicSlabSDs+slabNo), //its logical volume
                    slabName,               //its name
                    *logicWorld,            //its mother (logical) volume
                    false,                  //no boolean operations
                    0,                      //its copy number 
                    false);                  //checkOverlap

	// user limits 
	new (fStepLimits+slabNo) G4UserLimits(); 
	// photonuclear production
	G4double minEkine = 6.0*MeV;
	(fStepLimits+slabNo)->SetUserMinEkine(minEkine);
	// step limit 
	G4double stepMax = slab_pDz;
	(fStepLimits+slabNo)->SetMaxAllowedStep(stepMax);
	// set userlimits for slab
	(fLogicSlabSDs+slabNo)->SetUserLimits(fStepLimits+slabNo);

	// set color of region
  (fLogicSlabSDs+slabNo)->SetVisAttributes(new G4VisAttributes(G4Colour(0.0,0.0,1.-0.7*slabNo/fnSlabs)));  
} // ConstructSlab



void myDetectorConstruction::ConstructSDandField()
{

	//	Sensitive Detectors
	G4SDManager* SDman = G4SDManager::GetSDMpointer();

	G4VSensitiveDetector *slabSD;

	char slabName[50];
	char slabCollection[50]; 

	// iterate over sensitive detector slabs and 
	// register to G4SDManager
	for (G4int i=0; i<fnSlabs; i++){

		sprintf(slabName, "%s_Slab%02i", fInputPrefix->c_str(),i);
		sprintf(slabCollection, "Slab%02iHitsCollection", i);

		slabSD = new  myDetectorSD(slabName, slabCollection); 
		SDman->AddNewDetector(slabSD);
		(fLogicSlabSDs+i)->SetSensitiveDetector(slabSD);
	}

}
