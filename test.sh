#!/bin/bash
DIR='/home/team/lotteh'
while read p; do
  sudo cp $DIR/scripts/$p /usr/bin/$p
  sudo chmod a+x /usr/bin/$p
done < config/ascripts
sudo chmod a-x /usr/bin/setup
