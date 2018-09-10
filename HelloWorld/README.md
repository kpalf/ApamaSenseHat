# Apama SenseHat HelloWorld Python Plugin

This is a simple example showing that it is possible to drive a Raspberry Pi SenseHAT device from Apama EPL running in a Correlator process with a Python plugin for EPL.

## Prerequisites

**Hardware**
* Raspberry Pi version 3, Model B.  \(Untested but should also work with a v2, or v3+, but will NOT work with a v1 or a Zero or ZeroW.  Apama needs at least ARMv7hf\)
* SenseHAT
* Usual misc power, networking, cables
* For the Sense Hat install 'I2C' should be enabled in the 'interfaces' section of raspi-config. ( sudo raspi-config - option 5 then P5 )

**Software**
* [Apama Core Community Edition](http://apamacommunity.com) v10.3.0 \(Oct 2018 release\), or later, for Linux on ARM 
* Linux installation on the RaspberryPi.  Tested on Raspbian
* Python 3.6 - This is the tricky part as Raspian Jessie has 3.5, and Stretch has 3.5, so you need to build from source \(remember to build the shared version so it can be loaded in-process\)
* Python drivers for the SenseHAT.  Due to the Python 3.6 issues, this also needs rebuilding.


### Building and setting up Python 3.6
I was loosely following these [instructions](https://bohdan-danishevsky.blogspot.com/2017/01/building-python-360-on-raspberry-pi-3.html), with some deviations.
Notably, I wanted Python 3.6 \(3.6.6 at the time\), we need a shared library \(--enable-shared\), and I didn't want to disrupt the rest of the install on the Pi, so I did an "altinstall" instead of an "install" - so it goes in /usr/local.

```
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get -y install libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl

cd ~
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar -zxvf Python-3.6.6.tgz
cd Python-3.6.6
./configure --enable-shared
make -j4
sudo make altinstall
```

This version of python can now be executed with the specific command "python3.6" rather than "python3" which would get you the systme installed one.

I also discovered that after a reboot I don't appear to have the shared library on the library path so you need a \(probably in your ~/.bashrc\):
```
export LD_LIBRARY_PATH=/usr/local/lib
```

### Using the newly built Python 3.6 from Apama EPL
Apama 10.3 and above have samples for using Python as a Foreign-Function-Call from EPL running in the Correlator.  When supplying your own Python installation, as is the case with Apama Core Community Edition, it is necessary to tell the correlator where to find Python by setting an environment variable.

Always remember to work in a correctly configured Apama environment by sourcing \(not executing\) the `$APAMA_HOME/bin/apama_env`

```
export AP_PYTHONHOME=/usr/local
```
It should now be possible to follow the examples that come with Apama at:
`$APAMA_HOME/apama-samples/correlator_plugin/python`

### Using the SenseHAT from Python 3.6
So, the Python drivers for the SenseHAT are normally pretty easy to install for use with the system default Python \(3.4 on Jessie, 3.5 on Stretch\), but we want to use them from our freshly built Python 3.6, so it takes a little extra effort, but thankfully not too long.
This is what I did, by taking hints from various other articles and search results.

Lets start with the basics, as decribed at [the main documentation site](https://www.raspberrypi.org/documentation/hardware/sense-hat/).
First, I checked that the default SenseHAT drivers were installed:
```
sudo apt-get update
sudo apt-get install sense-hat
sudo reboot
```
There are samples in `/usr/src/sense-hat/examples`, but for my purpose I simply created a file called `sensehat_helloworld.py` with the following content:
```python
from sense_hat import SenseHat
sense = SenseHat()
sense.show_message("Hello world!")
```

... and tested it worked with `python sensehat_helloworld.py` which used the system installed Python.  A copy is available in the `pure_python` folder of this repo.

If you were to try to execute the same thing with your `python3.6` you'd find you would get a bunch of error messages that essentially say `ModuleNotFoundError`. So, now that we have confirmed it definitely works with the system installed Python, but not with our new Python3.6 we need to get the SenseHAT drivers installed there too.  Unfortunately, this means we need to build and ensure the dependencies are there.  The longest part is the compilation of the native parts of numpy, but its all scripted behind the scenes for us. The drivers also depend on a framework called "Pillow" which in turn need libjpeg-dev.
\(Some clues taken from: (https://github.com/RPi-Distro/python-sense-hat/issues/58) \)

Disclaimer: I haven't had a chance to try these instructions again on a clean Raspbian, they are from my notes.

```
sudo -s
export LD_LIBRARY_PATH=/usr/local/lib
apt install libopenjp2-7
apt-get install libjpeg-dev
pip3.6 install sense-hat rtimulib

pushd ~
git clone https://github.com/RPi-Distro/RTIMULib/ RTIMU
cd RTIMU/Linux/python
python3.6 setup.py build
python3.6 setup.py install
popd
```
\(I don't think if after this I had to do `pip3.6 install rtimulib` again, but below was the output\)
```
# pip3.6 install sense-hat rtimulib
	Requirement already satisfied: sense-hat in /usr/local/lib/python3.6/site-packages (2.2.0)
	Requirement already satisfied: rtimulib in /usr/local/lib/python3.6/site-packages (7.2.1)
	Requirement already satisfied: numpy in /usr/local/lib/python3.6/site-packages (from sense-hat) (1.15.1)
	Requirement already satisfied: pillow in /usr/local/lib/python3.6/site-packages (from sense-hat) (5.2.0)
```

Now when you try to repeat the `python3.6 sensehat_helloworld.py` you should find it works.

Great!  Now we have done all the hard work and Python3.6 can drive the SenseHAT.  The easy part is now to use that from Apama EPL running in the correlator.

### Using the SenseHAT, via Python 3.6, from Apama EPL.
As you will see from this example project, we just need 3 simple files:
1. A python file exposing a method that will be invoked from the EPL. This is the "plugin".  See the "plugins" folder.
2. A simple correlator configuration \(YAML\) file that names the pluging, and details the python filename, and class name within that file.  This is the "glue" that exposes the plugin to the EPL. See the "config" folder.
3. The EPL file \(normally/convensionally a ".mon" extension, but can be anything\) that will be "injected" into the running correlator and which imports the named plugin and invokes methods on it as needed. See the "monitorscript" folder.

Now let's try it in Apama.
> We did this earlier, but ensure that both `LD_LIBRARY_PATH=/usr/local/lib`, and `AP_PYTHONHOME=/usr/local` are configured in the environment where you have sourced `apama_env` and will start the correlator.

* In one apama shell start the correlator \(assuming current working directory is the root of this repo where this README is located\):
```
correlator --config epl/config/CorrelatorConfig.yaml
```

* In a second apama shell, use the `engine_inject` command to inject the EPL file into the running correlator.  It will execute immediately and invoke the python plugin to show the message on the SenseHAT.
```
engine_inject epl/monitors/SenseHat_HelloWorldPlugin.mon
```

---
Copyright \(c\) 2018 Kevin Palfreyman

