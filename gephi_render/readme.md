#catalog-network.jar

Wrapper for the gehpi-toolkit library that runs the force atlas 2 layout on a supplied GEXF file from the command line. This is a option for rendering very large networks that could not be handled by the Gephi GUI interface (100,000+ of nodes). The layout will run and output multiple files:

`io_gexf_latest.gexf` - the result XML file. Includes the X/Y position of each node as a result of the layout simulation. Produced after evey 500 tick.

`autolayout.pdf` - a PDF preview of the network produced every 20 ticks.

`tick_XX.png` - a PNG snapshop of the network produced every 20 ticks.

To run:

`java -jar catalog-network.jar -file path/to/file.gexf` 


You can pass options to controle the layout from the command line which are the same settings found in the Gephi interface:

-file the path to the gefx file eg -file ../../test.gefx

-linlogmode use lin log mode, boolean eg: -linlogmode true (default true)

-edgeweight edge weight influence, double eg: -edgeweight 1.0 (default 1.0)

-scalingratio node repulsion strength, double eg: -scalingratio 4.0 (default 4.0)

-stronggravity use strong gravity, boolean eg: -stronggravity true (default true)

-gravity gravity strength, double eg: -gravity 0.5 (default 0.02)

-threads how many cpu threads to use, int eg: -threads 8 (default 4)

-bhoptimize use Barnes Hut Optimize allows larger graphs, boolean eg: -bhoptimize true (default true)

-bhtheta  Barnes Hut Optimize theta, double eg: -bhtheta 2.0 (default 1.2)


For example, to make the nodes repulse more (expand away from eachother) you would pass a larger -scalingratio value, for example:

`java -jar catalog-network.jar -file path/to/file.gexf -scalingratio 8.0` 

The key purpose of this tool is to generate the final .gexf file that can be used to draw a large graph programmicly based on the X/Y, Size and Color (modularity) in produced as a result the layout process.
 

