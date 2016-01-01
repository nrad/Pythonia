<workspace name="02_midinotein"><referencesModules><moduleReference description="Saw oscillator (aplitude 1)" name="sound sources/SawVco"><input><vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/><vardef csType="k" description="Shape of wave, sawtooth/triangle/ramp" max="0.999" min="0.001" name="shape"/></input><output><vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/></output><opcode>/* Saw oscillator */
opcode SawVco, a, kk
  kfrq, kshape xin

  kfrq     limit     kfrq, 0, 50000
  kshape   limit     kshape, 0.001, 0.999
  aout     vco2      1, kfrq, 4, kshape

  xout aout
endop
  </opcode></moduleReference><moduleReference description="Amplify audio signal" name="amps mixers/Amp"><input><vardef csType="a" description="Audio signal" name="in"/><vardef csType="k" description="Gain" name="gain"/></input><output><vardef csType="a" description="Amplified audio signal" name="out"/></output><opcode>/* Amplify audio signal */
opcode Amp, a, ak
  ain, kgain xin
  aout = ain * kgain
  xout aout
endop
  </opcode></moduleReference><moduleReference description="Output mono signal to sound card" name="input output/PcmMonoOut"><input><vardef csType="a" description="Audio input" name="in"/></input><opcode>/* Output mono signal to sound card */
opcode PcmMonoOut, 0, a
  ain xin
     out ain
endop
  </opcode></moduleReference><moduleReference description="Midi input of frequency, note number, velocity and channel aftertouch" name="control/MidiNoteIn"><input><vardef csType="i" description="Scaling of MIDI velocity" max="32000.0" min="0.0" name="velscale"/><vardef csType="i" description="Minimal value for scaled channel aftertouch" name="minafttch"/><vardef csType="i" description="Maximal value for scaled channel aftertouch" name="maxafttch"/></input><output><vardef csType="k" description="Frequency of MIDI note with pitch bend information" name="frq"/><vardef csType="k" description="MIDI note number of last pressed key" name="note"/><vardef csType="i" description="Velocity of MIDI note" name="vel"/><vardef csType="k" description="Scaled channel aftertouch" name="afttch"/></output><opcode>/* Midi keyboard input of note number and velocity */
opcode MidiNoteIn, kkik, iii
  ivelscale, iminafttch, imaxafttch xin

  knote init 0
  kvel init 0
  kafttch init 0

  midinoteonkey knote, kvel
  midichannelaftertouch kafttch, iminafttch, imaxafttch
  kfrq cpsmidib
  ivel ampmidi  ivelscale

  xout kfrq, knote, ivel, kafttch
endop
  </opcode></moduleReference></referencesModules><instancesModules><moduleInstance id="1" name="sound sources/SawVco" xPos="187" yPos="25"><inputs><val description="Frequency of oscillator" id="0" value="200.0"/><val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/></inputs></moduleInstance><moduleInstance id="2" name="amps mixers/Amp" xPos="319" yPos="24"><inputs><val description="Audio signal" id="0" value="0"/><val description="Gain" id="1" value="25000.0"/></inputs></moduleInstance><moduleInstance id="3" name="input output/PcmMonoOut" xPos="429" yPos="26"><inputs><val description="Audio input" id="0" value="0"/></inputs></moduleInstance><moduleInstance id="4" name="control/MidiNoteIn" xPos="16" yPos="21"><inputs><val description="Scaling of MIDI velocity" id="0" value="15000.0"/><val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/><val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/></inputs></moduleInstance></instancesModules><connections><connection inModule="2" inputNum="0" outModule="1" outputNum="0"/><connection inModule="3" inputNum="0" outModule="2" outputNum="0"/><connection inModule="1" inputNum="0" outModule="4" outputNum="0"/></connections><additionalInfo><param name="actualModule" value=""/><param name="lastModuleId" value="4"/></additionalInfo></workspace>