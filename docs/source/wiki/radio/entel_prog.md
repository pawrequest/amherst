# Programming Entel Fleets

## Introduction
The DEFAULT24.efl `Fleet` has been preconfigured with our default settings and has one DX482 and one DX485 pre-populated.  

For simple 482-only jobs it will be enough to load the default fleet and begin programming the existing 482 profile to all radios.

For jobs involving 485s or custom settings we will save the default fleet with a new name and make edits


- Load DEFAULT24.efl from <a href="file://///amherstmain/radio%20programming/data%20files/Entel">Entel Fleets Dir</a>

-------------------------

## Prepare Fleet File

**if only using DX482s, and all settings are default / no emergency:**

- skip to [Write Data To Radios](prog-target) (program each radio with the only profile)


**if only using one of 482s or 485s:**

- delete the unused radio-type

**if using 485, or need emergency / custom settings:**

- save with new name
- continue through all sections


------------------------------------------------------------

## Configure Pools
`Pools` are top-level organisers. They determine what is available to the `Zones` we will allocate to specific radios. 
You can not eg manually add channels to a radio without first adding to the `Channels Pool`

### RF Channel pool
A `Channel` is a combination of *Alias*, *Frequency*, *Colour Code*, etc
- Check / set channel data for every `Channel` you may need
- 'Assign selected channel to all zones if appropriate

### Contacts Pool
A `Contact` is an `Individual` or `Group`, and has a *Name*, *Ident*, and (unused) *Calltype*
We will make a contact for each user and each group of users.

For each `Group` and `Individual` in the fleet: 
- Set *Name* and (automated) *Ident*
- 'Assign to all Zones' if appropriate
	 
	
### Emergency pool
add emergency profiles for each configuration you want available in the `Zones`, eg ManDown / LoneWorker / Panic Alarm

### Zones
Create a zone for each collection of RX groups (if multiple groups)
eg, with groups All, ADMIN, and USER, we create zones same name.

ALL zone would have radios not in any group and only receive calls made to ALL.
ADMIN zone has ALL and ADMIN rx groups
USER zone has ALL and USER rx groups


---------------------------


## Configure First Radio
Double click existing radio in pane on left of screen to configure it as a base to clone from

### Channel Preset Tab
Activate required zone/s for the individual radio 
For each channel in the Zone check that
	- frequencies are correct
	- (default) tx contact is correct i.e 'all' for simple fleets, or subgroup if complex ones.
	- rx group - The `Group` the radio is listening to
	- tx emergency - emergency profile or None

### General Info Tab
Contact pool should match with a username - click 'Use as radio alias' if neccessary  
Set boot zone - this is the default zone the radio boots into.

### Button Layout Tab
Configure buttons.
standard is to use orange button on top (long-press) for emergency on
and blue button on side (long-press) for emergency off

### Contact List Tab
- check all groups and users have been added to the radio
- clone all user and all groups to all radios

**IDIOT CHECK EVERYTHING NOW because now we clone it loads of times...**	

-------------------------------

## Add More Radios To Fleet.
* fleet -> add radio, clone closest matching existing unit
* if same zone/group settings for all radios then click 'use radio alias'
* if complex fleet create a base-radio with required Zones configured for each group
* repeat until all radios added

-------------------------------------
(prog-target)=
## Write Data To Radios 
programming window (utilites -> programming window)  
* connect a radio
* check / upgrade firmware if required
* select a personality from the drop down and hit write
* ignore wrong-serial warning
* ignore firmware-version warning (probably)
	

**PUT THE ACC-PORT COVER BACK ON!!!!**


