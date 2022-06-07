# RoboticsObjectDetection

Simple OpenCV Baseline: https://www.youtube.com/watch?v=HXDD7-EnGBY&ab_channel=Murtaza%27sWorkshop-RoboticsandAI

# Robot Control
The packages used to control the robot can be found on the documentation page:

https://docs.sunfounder.com/projects/picar-x/en/latest/python/python_start/download_and_run_code.html

# Usage

To run the main script with a red ball, simply use the following command:

```
python Main/bounce.py --rendering --ball_color red
```

The command posses two parameters. If you would like a live camera feed of the robot camera, use `--rendering`,
but we do not advise using rendering when actually testing the robot, as it makes the object detection much slower.
Additionally, you can specify a different ball color using `--ball_color "color"`, replacing `"color"` which one 
of the available options (blue/green/yellow/red/pink/purple).