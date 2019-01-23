#!/usr/bin/env python
import rospy
import sys   
import math  # used for - atan2 , pow and sqrt

# Importing message of type Twist
from geometry_msgs.msg import Twist 

# Importing message of type Pose
from turtlesim.msg import Pose      

class TurtleWaipoint(object):
    """Class to guide the turtle to the specified waypoint."""

    def __init__(self, waypoint_x=None, waypoint_y=None):
        """Class constructor."""
        # Init all variables
        # Current turtle position
        self.x = None
        self.y = None
        self.theta = None
        # Tolerance to reach waypoint.User Define
        self.tolerance = 0.3    
        # A position was received
        self.got_position = False
        # Reached position
        self.finished = False

        # ROS init
        rospy.init_node('turtle_waypoint')
        # Define pulisher: topic name, message type with queue size, To send velocity commands
        self.pub = rospy.Publisher('/turtle1/cmd_vel',Twist, queue_size=10)
        # Define subscriber: topic name, message type, function callback, to recieve Pose of the turtle 
        self.sub = rospy.Subscriber('/turtle1/pose',Pose,self.callback)

        # Retrieve waypoint
        self.waypoint_x = waypoint_x # User defined waypoint as argument 1 
        self.waypoint_y = waypoint_y # User defined waypoint as argument 2
        
        # Checking Param Server, the waypoints are not passed in the argument  
        if waypoint_x is None or waypoint_y is None:
            # No waypoint specified => look at the param server
            if rospy.has_param('/default_x') and rospy.has_param('/default_y'):# Expression for checking param server has waypoints or not
                print("Waypoints - Param Server")
                # Saving params from param server
                self.waypoint_x = rospy.get_param('/default_x')  # Fetching value of x from param server
                self.waypoint_y = rospy.get_param('/default_y')  # Fetching value of y from param server
            else:
                # No waypoint in param server => finish
                print("No waypoint found in param server")
                exit(1)
        # Showing the waypoint
        print('Heading to: {:.2f}, {:.2f}'.format(self.waypoint_x,
                                                  self.waypoint_y))
    # Defination of call back function 
    def callback(self, msg):
        """Saves the tutle position when a message is received."""
        # Storing the position in self.x, self.y and self.theta variables.
        self.x = msg.x  
        self.y = msg.y  
        self.theta = msg.theta
        self.got_position = True 
     
    def iterate(self): 
        """Keeps sending control commands to turtle until waypoint reached."""
        if self.finished:
            print('Congrats Waypoint reached and the turtle is at the goal')
            exit(0)
        else:
            # We know where we are
            if self.got_position:
                dist = math.sqrt( math.pow( (self.x - self.waypoint_x),2) + math.pow( (self.y -self.waypoint_y),2)  )
                # Checking if we have reached gaol
                if dist < self.tolerance:  
                    # If Waypoint or goal is reached Finish the loop
                    self.finished = True
                else:
                    print('Moving...')
		            command_vel = Twist()
                
                    # Proportional control of the linear x velocity of the turtle
                    command_vel.linear.x = 0.5 * ( dist)
                    command_vel.linear.y = 0  
                    command_vel.linear.z = 0
		            command_vel.angular.x = 0
                    command_vel.angular.y = 0

                    # Finding the deviation of angle of the robto and assigning turning velocity
                    command_vel.angular.z =  3.8* (math.atan2( self.waypoint_y - self.y  , self.waypoint_x - self.x  ) - self.theta );
	                self.pub.publish(command_vel)# Publishing the values stored in the variable till we reach to the goal.
                    


if __name__ == '__main__':
    # Check commandline inputs
    if not len(sys.argv) == 3:
        # Case when no input waypoint specified
        print('No waypoint specified in commandline')
        node = TurtleWaipoint()
    else:
        node = TurtleWaipoint(float(sys.argv[1]), float(sys.argv[2])) # Passing Waypoints/arguments defined by the user through terminal.
    # Run forever
    while not rospy.is_shutdown():
        node.iterate() # Calling iterative fucntion for goal validity
        rospy.sleep(0.3) # Pause timings 
    print('\nROS shutdown')
