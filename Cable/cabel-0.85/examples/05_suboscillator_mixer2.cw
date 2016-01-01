<workspace name="05_suboscillator_mixer2"><referencesModules><moduleReference description="Saw oscillator (aplitude 1)" name="sound sources/SawVco"><input><vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/><vardef csType="k" description="Shape of wave, sawtooth/triangle/ramp" max="0.999" min="0.001" name="shape"/></input><output><vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/></output><opcode>/* Saw oscillator */
opcode SawVco, a, kk
  kfrq, kshape xin

  kfrq     limit     kfrq, 0, 50000
  kshape   limit     kshape, 0.001, 0.999
  aout     vco2      1, kfrq, 4, kshape

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
  </opcode></moduleReference><moduleReference description="Mixer for two audio signals" name="amps mixers/Mixer2"><input><vardef csType="a" description="First audio rate signal" name="in1"/><vardef csType="k" description="Amplitude multiplicator for in1" min="0.0" name="gain1"/><vardef csType="a" description="Second audio rate signal" name="in2"/><vardef csType="k" description="Amplitude multiplicator for in2" min="0.0" name="gain2"/></input><output><vardef csType="a" description="Mixed input signals" name="out"/></output><opcode>/* Mixer for two audio signals */
opcode Mixer2, a, akak
  ain1, kgain1, ain2, kgain2 xin
  aout = ain1*kgain1 + ain2*kgain2
  xout aout
endop
  </opcode></moduleReference><moduleReference description="Multiply two control signals" name="maths/ControlMultiply"><input><vardef csType="k" description="First control signal" name="in1"/><vardef csType="k" description="Second control signal" name="in2"/></input><output><vardef csType="k" description="Product of input signals" name="pro"/></output><opcode>/* Multiply two control signals */
opcode ControlMultiply, k, kk
  kin1, kin2 xin
  kpro = kin1 * kin2
  xout kpro
endop
  </opcode></moduleReference><moduleReference description="Square oscillator (amplitude 1)" name="sound sources/SquareVco"><input><vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/><vardef csType="k" description="Pulse width of square wave" max="0.999" min="0.001" name="pw"/></input><output><vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/></output><opcode>/* Square oscillator */
opcode SquareVco, a, kk
  kfrq, kpw xin

  kfrq     limit     kfrq, 0, 50000
  kpw      limit     kpw, 0.001, 0.999
  aout     vco2      1, kfrq, 2, kpw

  xout aout
endop
  </opcode></moduleReference><moduleReference description="Amplify audio signal" name="amps mixers/Amp"><input><vardef csType="a" description="Audio signal" name="in"/><vardef csType="k" description="Gain" name="gain"/></input><output><vardef csType="a" description="Amplified audio signal" name="out"/></output><opcode>/* Amplify audio signal */
opcode Amp, a, ak
  ain, kgain xin
  aout = ain * kgain
  xout aout
endop
  </opcode></moduleReference></referencesModules><instancesModules><moduleInstance id="1" name="sound sources/SawVco" xPos="197" yPos="12"><inputs><val description="Frequency of oscillator" id="0" value="200.0"/><val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/></inputs></moduleInstance><moduleInstance id="3" name="input output/PcmMonoOut" xPos="653" yPos="22"><inputs><val description="Audio input" id="0" value="0"/></inputs></moduleInstance><moduleInstance id="4" name="control/MidiNoteIn" xPos="13" yPos="20"><inputs><val description="Scaling of MIDI velocity" id="0" value="20000.0"/><val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/><val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/></inputs></moduleInstance><moduleInstance id="5" name="modulators/AdsrLinMidi" xPos="452" yPos="152"><inputs><val description="Amplitude scale factor" id="0" value="1.0"/><val description="Attack time in seconds" id="1" value="0.1"/><val description="Decay time in seconds" id="2" value="0.2"/><val description="Sustain level" id="3" value="0.7"/><val description="Release time in seconds" id="4" value="0.2"/></inputs></moduleInstance><moduleInstance id="6" name="filters/MoogVcf" xPos="460" yPos="23"><inputs><val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/><val description="Filter cut-off frequency" id="1" value="2000.0"/><val description="Filter resonance (self-resonates at 1)" id="2" value="0.5"/></inputs></moduleInstance><moduleInstance id="7" name="modulators/AdsrLinMidi" xPos="326" yPos="109"><inputs><val description="Amplitude scale factor" id="0" value="15000.0"/><val description="Attack time in seconds" id="1" value="0.01"/><val description="Decay time in seconds" id="2" value="0.3"/><val description="Sustain level" id="3" value="0.2"/><val description="Release time in seconds" id="4" value="0.2"/></inputs></moduleInstance><moduleInstance id="8" name="amps mixers/Mixer2" xPos="341" yPos="14"><inputs><val description="First audio rate signal" id="0" value="0"/><val description="Amplitude multiplicator for in1" id="1" value="0.8"/><val description="Second audio rate signal" id="2" value="0"/><val description="Amplitude multiplicator for in2" id="3" value="0.4"/></inputs></moduleInstance><moduleInstance id="9" name="maths/ControlMultiply" xPos="162" yPos="79"><inputs><val description="First control signal" id="0" value="1.0"/><val description="Second control signal" id="1" value="0.5"/></inputs></moduleInstance><moduleInstance id="10" name="sound sources/SquareVco" xPos="173" yPos="140"><inputs><val description="Frequency of oscillator" id="0" value="0"/><val description="Pulse width of square wave" id="1" value="0.5"/></inputs></moduleInstance><moduleInstance id="11" name="amps mixers/Amp" xPos="552" yPos="23"><inputs><val description="Audio signal" id="0" value="0"/><val description="Gain" id="1" value="0"/></inputs></moduleInstance></instancesModules><connections><connection inModule="1" inputNum="0" outModule="4" outputNum="0"/><connection inModule="5" inputNum="0" outModule="4" outputNum="2"/><connection inModule="6" inputNum="1" outModule="7" outputNum="0"/><connection inModule="11" inputNum="1" outModule="5" outputNum="0"/><connection inModule="3" inputNum="0" outModule="11" outputNum="0"/><connection inModule="11" inputNum="0" outModule="6" outputNum="0"/><connection inModule="6" inputNum="0" outModule="8" outputNum="0"/><connection inModule="8" inputNum="0" outModule="1" outputNum="0"/><connection inModule="9" inputNum="0" outModule="4" outputNum="0"/><connection inModule="10" inputNum="0" outModule="9" outputNum="0"/><connection inModule="8" inputNum="2" outModule="10" outputNum="0"/></connections><additionalInfo><param name="actualModule" value=""/><param name="lastModuleId" value="11"/></additionalInfo></workspace>