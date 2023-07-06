#!/bin/bash

BAG_NAME=$1

sleep 5s
gnome-terminal -x bash -c "rosbag reindex ${BAG_NAME};exec bash"
sleep 5s
gnome-terminal -x bash -c "rosbag fix --force ${BAG_NAME} fix1.bag;exec bash"
