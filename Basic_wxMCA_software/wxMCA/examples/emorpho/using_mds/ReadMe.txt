Bridgeport Instruments, LLC, 2019-09-19

These are data acquisition examples where you access the eMorpho device through the Morpho Data Server.

The client uses ZMQ (www.zeromq.org) as the protocol layer on top of TCP/IP/.

While the example clients are written in Python, the user can write their client in any of more than 40+ programming languages, including the obvious such as C/C++/C#, Java, PHP to R to the more obscure such as Erlang and Haskell.  Visit ZMQ (www.zeromq.org) to find a ZMQ binding for your favorite language.

Before you run any of the examples, make sure the Morpho Data Server (../../mds_v3/eMorpho_server.py) is running.

If you want to test the software without having eMorpho hardware connected to your computer, make sure the Morpho Simulation Server (../../sim_v3/eMorpho_server.py) is running.

Note that you cannot run the real MDS and the simulator at the same time.

