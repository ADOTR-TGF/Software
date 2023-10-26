# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/enp/geant4/simulations/Neutron-stage1

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/enp/geant4/simulations/Neutron-stage1-build

# Include any dependencies generated for this target.
include CMakeFiles/run.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/run.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/run.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/run.dir/flags.make

CMakeFiles/run.dir/main.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/main.cc.o: /home/enp/geant4/simulations/Neutron-stage1/main.cc
CMakeFiles/run.dir/main.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/run.dir/main.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/main.cc.o -MF CMakeFiles/run.dir/main.cc.o.d -o CMakeFiles/run.dir/main.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/main.cc

CMakeFiles/run.dir/main.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/main.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/main.cc > CMakeFiles/run.dir/main.cc.i

CMakeFiles/run.dir/main.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/main.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/main.cc -o CMakeFiles/run.dir/main.cc.s

CMakeFiles/run.dir/src/myActionInitialization.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myActionInitialization.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myActionInitialization.cc
CMakeFiles/run.dir/src/myActionInitialization.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/run.dir/src/myActionInitialization.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myActionInitialization.cc.o -MF CMakeFiles/run.dir/src/myActionInitialization.cc.o.d -o CMakeFiles/run.dir/src/myActionInitialization.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myActionInitialization.cc

CMakeFiles/run.dir/src/myActionInitialization.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myActionInitialization.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myActionInitialization.cc > CMakeFiles/run.dir/src/myActionInitialization.cc.i

CMakeFiles/run.dir/src/myActionInitialization.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myActionInitialization.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myActionInitialization.cc -o CMakeFiles/run.dir/src/myActionInitialization.cc.s

CMakeFiles/run.dir/src/myDetectorConstruction.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myDetectorConstruction.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorConstruction.cc
CMakeFiles/run.dir/src/myDetectorConstruction.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/run.dir/src/myDetectorConstruction.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myDetectorConstruction.cc.o -MF CMakeFiles/run.dir/src/myDetectorConstruction.cc.o.d -o CMakeFiles/run.dir/src/myDetectorConstruction.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorConstruction.cc

CMakeFiles/run.dir/src/myDetectorConstruction.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myDetectorConstruction.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorConstruction.cc > CMakeFiles/run.dir/src/myDetectorConstruction.cc.i

CMakeFiles/run.dir/src/myDetectorConstruction.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myDetectorConstruction.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorConstruction.cc -o CMakeFiles/run.dir/src/myDetectorConstruction.cc.s

CMakeFiles/run.dir/src/myDetectorHit.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myDetectorHit.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorHit.cc
CMakeFiles/run.dir/src/myDetectorHit.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object CMakeFiles/run.dir/src/myDetectorHit.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myDetectorHit.cc.o -MF CMakeFiles/run.dir/src/myDetectorHit.cc.o.d -o CMakeFiles/run.dir/src/myDetectorHit.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorHit.cc

CMakeFiles/run.dir/src/myDetectorHit.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myDetectorHit.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorHit.cc > CMakeFiles/run.dir/src/myDetectorHit.cc.i

CMakeFiles/run.dir/src/myDetectorHit.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myDetectorHit.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorHit.cc -o CMakeFiles/run.dir/src/myDetectorHit.cc.s

CMakeFiles/run.dir/src/myDetectorSD.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myDetectorSD.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorSD.cc
CMakeFiles/run.dir/src/myDetectorSD.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Building CXX object CMakeFiles/run.dir/src/myDetectorSD.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myDetectorSD.cc.o -MF CMakeFiles/run.dir/src/myDetectorSD.cc.o.d -o CMakeFiles/run.dir/src/myDetectorSD.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorSD.cc

CMakeFiles/run.dir/src/myDetectorSD.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myDetectorSD.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorSD.cc > CMakeFiles/run.dir/src/myDetectorSD.cc.i

CMakeFiles/run.dir/src/myDetectorSD.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myDetectorSD.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myDetectorSD.cc -o CMakeFiles/run.dir/src/myDetectorSD.cc.s

CMakeFiles/run.dir/src/myEventAction.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myEventAction.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myEventAction.cc
CMakeFiles/run.dir/src/myEventAction.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Building CXX object CMakeFiles/run.dir/src/myEventAction.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myEventAction.cc.o -MF CMakeFiles/run.dir/src/myEventAction.cc.o.d -o CMakeFiles/run.dir/src/myEventAction.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myEventAction.cc

CMakeFiles/run.dir/src/myEventAction.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myEventAction.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myEventAction.cc > CMakeFiles/run.dir/src/myEventAction.cc.i

CMakeFiles/run.dir/src/myEventAction.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myEventAction.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myEventAction.cc -o CMakeFiles/run.dir/src/myEventAction.cc.s

CMakeFiles/run.dir/src/myGammaPhysics.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myGammaPhysics.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myGammaPhysics.cc
CMakeFiles/run.dir/src/myGammaPhysics.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_7) "Building CXX object CMakeFiles/run.dir/src/myGammaPhysics.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myGammaPhysics.cc.o -MF CMakeFiles/run.dir/src/myGammaPhysics.cc.o.d -o CMakeFiles/run.dir/src/myGammaPhysics.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myGammaPhysics.cc

CMakeFiles/run.dir/src/myGammaPhysics.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myGammaPhysics.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myGammaPhysics.cc > CMakeFiles/run.dir/src/myGammaPhysics.cc.i

CMakeFiles/run.dir/src/myGammaPhysics.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myGammaPhysics.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myGammaPhysics.cc -o CMakeFiles/run.dir/src/myGammaPhysics.cc.s

CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myHadronElasticPhysicsHP.cc
CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_8) "Building CXX object CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o -MF CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o.d -o CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myHadronElasticPhysicsHP.cc

CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myHadronElasticPhysicsHP.cc > CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.i

CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myHadronElasticPhysicsHP.cc -o CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.s

CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPMessenger.cc
CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_9) "Building CXX object CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o -MF CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o.d -o CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPMessenger.cc

CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPMessenger.cc > CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.i

CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPMessenger.cc -o CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.s

CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPphysics.cc
CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_10) "Building CXX object CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o -MF CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o.d -o CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPphysics.cc

CMakeFiles/run.dir/src/myNeutronHPphysics.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myNeutronHPphysics.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPphysics.cc > CMakeFiles/run.dir/src/myNeutronHPphysics.cc.i

CMakeFiles/run.dir/src/myNeutronHPphysics.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myNeutronHPphysics.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myNeutronHPphysics.cc -o CMakeFiles/run.dir/src/myNeutronHPphysics.cc.s

CMakeFiles/run.dir/src/myPhysicsList.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myPhysicsList.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myPhysicsList.cc
CMakeFiles/run.dir/src/myPhysicsList.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_11) "Building CXX object CMakeFiles/run.dir/src/myPhysicsList.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myPhysicsList.cc.o -MF CMakeFiles/run.dir/src/myPhysicsList.cc.o.d -o CMakeFiles/run.dir/src/myPhysicsList.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myPhysicsList.cc

CMakeFiles/run.dir/src/myPhysicsList.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myPhysicsList.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myPhysicsList.cc > CMakeFiles/run.dir/src/myPhysicsList.cc.i

CMakeFiles/run.dir/src/myPhysicsList.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myPhysicsList.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myPhysicsList.cc -o CMakeFiles/run.dir/src/myPhysicsList.cc.s

CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myPrimaryGeneratorAction.cc
CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_12) "Building CXX object CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o -MF CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o.d -o CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myPrimaryGeneratorAction.cc

CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myPrimaryGeneratorAction.cc > CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.i

CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myPrimaryGeneratorAction.cc -o CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.s

CMakeFiles/run.dir/src/myRunAction.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myRunAction.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myRunAction.cc
CMakeFiles/run.dir/src/myRunAction.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_13) "Building CXX object CMakeFiles/run.dir/src/myRunAction.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myRunAction.cc.o -MF CMakeFiles/run.dir/src/myRunAction.cc.o.d -o CMakeFiles/run.dir/src/myRunAction.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myRunAction.cc

CMakeFiles/run.dir/src/myRunAction.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myRunAction.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myRunAction.cc > CMakeFiles/run.dir/src/myRunAction.cc.i

CMakeFiles/run.dir/src/myRunAction.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myRunAction.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myRunAction.cc -o CMakeFiles/run.dir/src/myRunAction.cc.s

CMakeFiles/run.dir/src/myShielding.cc.o: CMakeFiles/run.dir/flags.make
CMakeFiles/run.dir/src/myShielding.cc.o: /home/enp/geant4/simulations/Neutron-stage1/src/myShielding.cc
CMakeFiles/run.dir/src/myShielding.cc.o: CMakeFiles/run.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_14) "Building CXX object CMakeFiles/run.dir/src/myShielding.cc.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/run.dir/src/myShielding.cc.o -MF CMakeFiles/run.dir/src/myShielding.cc.o.d -o CMakeFiles/run.dir/src/myShielding.cc.o -c /home/enp/geant4/simulations/Neutron-stage1/src/myShielding.cc

CMakeFiles/run.dir/src/myShielding.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/run.dir/src/myShielding.cc.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/enp/geant4/simulations/Neutron-stage1/src/myShielding.cc > CMakeFiles/run.dir/src/myShielding.cc.i

CMakeFiles/run.dir/src/myShielding.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/run.dir/src/myShielding.cc.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/enp/geant4/simulations/Neutron-stage1/src/myShielding.cc -o CMakeFiles/run.dir/src/myShielding.cc.s

# Object files for target run
run_OBJECTS = \
"CMakeFiles/run.dir/main.cc.o" \
"CMakeFiles/run.dir/src/myActionInitialization.cc.o" \
"CMakeFiles/run.dir/src/myDetectorConstruction.cc.o" \
"CMakeFiles/run.dir/src/myDetectorHit.cc.o" \
"CMakeFiles/run.dir/src/myDetectorSD.cc.o" \
"CMakeFiles/run.dir/src/myEventAction.cc.o" \
"CMakeFiles/run.dir/src/myGammaPhysics.cc.o" \
"CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o" \
"CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o" \
"CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o" \
"CMakeFiles/run.dir/src/myPhysicsList.cc.o" \
"CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o" \
"CMakeFiles/run.dir/src/myRunAction.cc.o" \
"CMakeFiles/run.dir/src/myShielding.cc.o"

# External object files for target run
run_EXTERNAL_OBJECTS =

run: CMakeFiles/run.dir/main.cc.o
run: CMakeFiles/run.dir/src/myActionInitialization.cc.o
run: CMakeFiles/run.dir/src/myDetectorConstruction.cc.o
run: CMakeFiles/run.dir/src/myDetectorHit.cc.o
run: CMakeFiles/run.dir/src/myDetectorSD.cc.o
run: CMakeFiles/run.dir/src/myEventAction.cc.o
run: CMakeFiles/run.dir/src/myGammaPhysics.cc.o
run: CMakeFiles/run.dir/src/myHadronElasticPhysicsHP.cc.o
run: CMakeFiles/run.dir/src/myNeutronHPMessenger.cc.o
run: CMakeFiles/run.dir/src/myNeutronHPphysics.cc.o
run: CMakeFiles/run.dir/src/myPhysicsList.cc.o
run: CMakeFiles/run.dir/src/myPrimaryGeneratorAction.cc.o
run: CMakeFiles/run.dir/src/myRunAction.cc.o
run: CMakeFiles/run.dir/src/myShielding.cc.o
run: CMakeFiles/run.dir/build.make
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4Tree.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4FR.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4GMocren.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4visHepRep.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4RayTracer.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4VRML.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4OpenGL.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4gl2ps.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4vis_management.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4modeling.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4interfaces.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4persistency.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4error_propagation.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4readout.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4physicslists.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4tasking.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4parmodels.so
run: /usr/lib/x86_64-linux-gnu/libGL.so
run: /usr/lib/x86_64-linux-gnu/libXmu.so
run: /usr/lib/x86_64-linux-gnu/libXext.so
run: /usr/lib/x86_64-linux-gnu/libXt.so
run: /usr/lib/x86_64-linux-gnu/libICE.so
run: /usr/lib/x86_64-linux-gnu/libSM.so
run: /usr/lib/x86_64-linux-gnu/libX11.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4run.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4event.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4tracking.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4processes.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4analysis.so
run: /usr/lib/x86_64-linux-gnu/libexpat.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4digits_hits.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4track.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4particles.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4geometry.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4materials.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4zlib.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4graphics_reps.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4intercoms.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4global.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4clhep.so
run: /home/enp/geant4/geant4-v10.7.3-install/lib/libG4ptl.so.0.0.2
run: CMakeFiles/run.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_15) "Linking CXX executable run"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/run.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/run.dir/build: run
.PHONY : CMakeFiles/run.dir/build

CMakeFiles/run.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/run.dir/cmake_clean.cmake
.PHONY : CMakeFiles/run.dir/clean

CMakeFiles/run.dir/depend:
	cd /home/enp/geant4/simulations/Neutron-stage1-build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/enp/geant4/simulations/Neutron-stage1 /home/enp/geant4/simulations/Neutron-stage1 /home/enp/geant4/simulations/Neutron-stage1-build /home/enp/geant4/simulations/Neutron-stage1-build /home/enp/geant4/simulations/Neutron-stage1-build/CMakeFiles/run.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/run.dir/depend

