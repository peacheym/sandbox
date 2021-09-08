/*
 ____  _____ _        _    
| __ )| ____| |      / \   
|  _ \|  _| | |     / _ \  
| |_) | |___| |___ / ___ \ 
|____/|_____|_____/_/   \_\

*/


#include <Bela.h>
#include <cmath>

#include <libraries/Trill/Trill.h>
#define NUM_TOUCH 5 // Number of touches on Trill sensor

// Include libmapper in this project
#include <mapper/mapper_cpp.h>

float gInterval = 0.5;
float gSecondsElapsed = 0;
int gCount = 0;

// libmapper object declarations
mapper::Device* dev;
mapper::Signal trill_touches;

// Trill object declaration
Trill touchSensor;

// Location of touches on Trill Bar
float gTouchLocation[NUM_TOUCH] = { 0.0, 0.0, 0.0, 0.0, 0.0 };
// Size of touches on Trill bar
float gTouchSize[NUM_TOUCH] = { 0.0, 0.0, 0.0, 0.0, 0.0 };
// Number of active touches
int gNumActiveTouches = 0;

// Sleep time for auxiliary task
unsigned int gTaskSleepTime = 12000; // microseconds
// Time period (in seconds) after which data will be sent to the GUI
float gTimePeriod = 0.015;

/*
* Function to be run on an auxiliary task that reads data from the Trill sensor.
* Here, a loop is defined so that the task runs recurrently for as long as the
* audio thread is running.
*/
void loop(void*)
{
	while(!Bela_stopRequested())
	{
		 // Read locations from Trill sensor
		 touchSensor.readI2C();
		 gNumActiveTouches = touchSensor.getNumTouches();
		 for(unsigned int i = 0; i < gNumActiveTouches; i++) {
			 gTouchLocation[i] = touchSensor.touchLocation(i);
			 gTouchSize[i] = touchSensor.touchSize(i);
			 
 			/*! Update libmapper signal instances !*/
 			// rt_printf("%f\n", gTouchSize[i]);
 			// trill_touches.instance(i).set_value(gTouchSize[i]);
 			std::array<float, 2>val = {{gTouchLocation[i], gTouchSize[i]}};
			trill_touches.instance(i).set_value(val);

		 }
		 // For all inactive touches, set location and size to 0
		 for(unsigned int i = gNumActiveTouches; i <  NUM_TOUCH; i++) {
			 gTouchLocation[i] = 0.0;
			 gTouchSize[i] = 0.0;
			 
 			/*! Update libmapper signal instances !*/
			trill_touches.instance(i).release();
		 }
		 usleep(gTaskSleepTime);
	}
}

/*
* Function to be run on an auxiliary task that polls a libmapper device for as long as the audio thread is running.
*/
void poll(void*)
{
	while(!Bela_stopRequested())
	{
		 dev->poll();
 		 usleep(gTaskSleepTime);
	}
}

bool setup(BelaContext *context, void *userData)
{
    rt_printf("This Bela project has started running!\n");
    
    float min = 0;
    float max = 1;
    int num_inst = NUM_TOUCH;
    
    // Instantiate libmapper device
    dev = new mapper::Device("bela");

	// Consider making this a 2D vector signal, one for position and one for size.
	// mapper::Signal trill_touches;
	trill_touches= dev->add_signal(mapper::Direction::OUTGOING, "trill-bar", 2, mapper::Type::FLOAT, "pos", &min, &max, &num_inst);

	while(!dev->ready()){
		dev->poll(500);
	}
	
	for (mapper::Signal sig : dev->signals()){
		rt_printf("Signal: ");
	}
	
	// Set and schedule aux task for handling libmapper device & signal updates.
	Bela_runAuxiliaryTask(poll);
	rt_printf("libmapper device is ready!\n");
	
	
	// Setup a Trill Bar sensor on i2c bus 1, using the default mode and address
	if(touchSensor.setup(1, Trill::BAR) != 0) {
		fprintf(stderr, "Unable to initialise Trill Bar\n");
		return false;
	}
	touchSensor.printDetails();
	
	// Set and schedule auxiliary task for reading sensor data from the I2C bus
	Bela_runAuxiliaryTask(loop);
	rt_printf("Trill Bar is ready!\n");

	return true;
}

void render(BelaContext *context, void *userData)
{
	/* Do nothing, for now. */
}

void cleanup(BelaContext *context, void *userData)
{
	/* Do nothing, for now. */
}
