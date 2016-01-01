<workspace name="04_moog_filter"><referencesModules><moduleReference description="Saw oscillator (aplitude 1)" name="sound sources/SawVco"><input><vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/><vardef csType="k" description="Shape of wave, sawtooth/triangle/ramp" max="0.999" min="0.001" name="shape"/></input><output><vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/></output><opcode>/* Saw oscillator */
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
  </opcode></moduleReference><moduleReference description="MIDI activated linear ADSR envelope" name="modulators/AdsrLinMidi"><input><vardef csType="i" description="Amplitude scale factor" name="amp"/><vardef csType="i" description="Attack time in seconds" min="0.0" name="atk"/><vardef csType="i" description="Decay time in seconds" min="0.0" name="dec"/><vardef csType="i" description="Sustain level" max="1.0" min="0.0" name="slev"/><vardef csType="i" description="Release time in seconds" min="0.0" name="rel"/></input><output><vardef csType="k" description="Envelope at control rate" name="env"/></output><opcode>/* MIDI activated linear ADSR envelope */
opcode AdsrLinMidi, k, iiiii
  iamp, iatk, idec, islev, irel xin

  kenv     madsr      iatk, idec, islev, irel
  kenv     =          iamp*kenv

  xout kenv
endop
  </opcode></moduleReference><moduleReference description="Moog lowpass filter, to avoid clipping use input signal with max amplitude 1" name="filters/MoogVcf"><input><vardef csType="a" description="Audio rate input, to avoid clipping use input signal with max amplitude 1" max="1.0" min="-1.0" name="in"/><vardef csType="k" description="Filter cut-off frequency" min="0.0" name="fco"/><vardef csType="k" description="Filter resonance (self-resonates at 1)" max="2.0" min="0.0" name="res"/></input><output><vardef csType="a" description="Filtered audio signal" name="out"/></output><opcode>/* Moog lowpass filter */
opcode MoogVcf, a, akk
  ain, kfco, kres  xin

  ain     limit ain, -1, 1
  kfco    limit kfco, 0, 50000
  kres    limit kres, 0, 2
  aout    moogvcf ain, kfco, kres

  xout aout
endop
  </opcode></moduleReference></referencesModules><instancesModules><moduleInstance id="1" name="sound sources/SawVco" xPos="187" yPos="25"><inputs><val description="Frequency of oscillator" id="0" value="200.0"/><val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/></inputs></moduleInstance><moduleInstance id="2" name="amps mixers/Amp" xPos="479" yPos="28"><inputs><val description="Audio signal" id="0" value="0"/><val description="Gain" id="1" value="25000.0"/></inputs></moduleInstance><moduleInstance id="3" name="input output/PcmMonoOut" xPos="592" yPos="23"><inputs><val description="Audio input" id="0" value="0"/></inputs></moduleInstance><moduleInstance id="4" name="control/MidiNoteIn" xPos="16" yPos="21"><inputs><val description="Scaling of MIDI velocity" id="0" value="20000.0"/><val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/><val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/></inputs></moduleInstance><moduleInstance id="5" name="modulators/AdsrLinMidi" xPos="356" yPos="124"><inputs><val description="Amplitude scale factor" id="0" value="1.0"/><val description="Attack time in seconds" id="1" value="0.1"/><val description="Decay time in seconds" id="2" value="0.2"/><val description="Sustain level" id="3" value="0.7"/><val description="Release time in seconds" id="4" value="0.2"/></inputs></moduleInstance><moduleInstance id="6" name="filters/MoogVcf" xPos="352" yPos="25"><inputs><val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/><val description="Filter cut-off frequency" id="1" value="2000.0"/><val description="Filter resonance (self-resonates at 1)" id="2" value="0.5"/></inputs></moduleInstance><moduleInstance id="7" name="modulators/AdsrLinMidi" xPos="217" yPos="95"><inputs><val description="Amplitude scale factor" id="0" value="15000.0"/><val description="Attack time in seconds" id="1" value="0.01"/><val description="Decay time in seconds" id="2" value="0.3"/><val description="Sustain level" id="3" value="0.2"/><val description="Release time in seconds" id="4" value="0.2"/></inputs></moduleInstance></instancesModules><connections><connection inModule="3" inputNum="0" outModule="2" outputNum="0"/><connection inModule="1" inputNum="0" outModule="4" outputNum="0"/><connection inModule="5" inputNum="0" outModule="4" outputNum="2"/><connection inModule="2" inputNum="1" outModule="5" outputNum="0"/><connection inModule="6" inputNum="0" outModule="1" outputNum="0"/><connection inModule="2" inputNum="0" outModule="6" outputNum="0"/><connection inModule="6" inputNum="1" outModule="7" outputNum="0"/></connections><additionalInfo><param name="actualModule" value="5"/><param name="lastModuleId" value="7"/></additionalInfo></workspace>