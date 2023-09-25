# Data_processing_tools
Data processing tools for RflyMAD dataset

if you want to run this code, please run python Rflytool_main.py first.

Firstly, you need to change the parse in the file, such as data restore path, choosing sub-dataset, fault types, flight statues and number of flight cases.

sub_dataset:

-1, all; 1, SIL; 2, HIL; 3, Real

Flight_status:

-1, all;

1, hover;

2, waypoints;

3, velocity control;

4, circling;

5, acceleration;

6, deceleration

Fault type:

-1, all

1, motor

2, propeller

3, low voltage

4, wind affect

5, load lose

6, accelerometer

7, gyroscope

8, magnetometer

9, barometer

10, GPS

11, no fault
