<?xml version="1.0" encoding="utf-8"?>
<workspace name="formant_aeiou">
	<referencesModules>
		<moduleReference description="Midi input of frequency, note number, velocity and channel aftertouch" name="control/MidiNoteIn">
			<input>
				<vardef csType="i" description="Scaling of MIDI velocity" max="32000.0" min="0.0" name="velscale"/>
				<vardef csType="i" description="Minimal value for scaled channel aftertouch" name="minafttch"/>
				<vardef csType="i" description="Maximal value for scaled channel aftertouch" name="maxafttch"/>
			</input>
			<output>
				<vardef csType="k" description="Frequency of MIDI note with pitch bend information" name="frq"/>
				<vardef csType="k" description="MIDI note number of last pressed key" name="note"/>
				<vardef csType="i" description="Velocity of MIDI note" name="vel"/>
				<vardef csType="k" description="Scaled channel aftertouch" name="afttch"/>
			</output>
			<opcode>
				/* Midi keyboard input of note number and velocity */
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
			</opcode>
		</moduleReference>
		<moduleReference description="Saw oscillator (aplitude 1)" name="sound sources/SawVco">
			<input>
				<vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/>
				<vardef csType="k" description="Shape of wave, sawtooth/triangle/ramp" max="0.999" min="0.001" name="shape"/>
			</input>
			<output>
				<vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/>
			</output>
			<opcode>
				/* Saw oscillator */
opcode SawVco, a, kk
  kfrq, kshape xin

  kfrq     limit     kfrq, 0, 50000
  kshape   limit     kshape, 0.001, 0.999
  aout     vco2      1, kfrq, 4, kshape

  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Output mono signal to sound card" name="input output/PcmMonoOut">
			<input>
				<vardef csType="a" description="Audio input" name="in"/>
			</input>
			<opcode>
				/* Output mono signal to sound card */
opcode PcmMonoOut, 0, a
  ain xin
     out ain
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Formant filter (be careful with amplitude of output)" name="filters/Formant">
			<input>
				<vardef csType="a" description="Audio rate input" name="in"/>
				<vardef csType="k" description="Filter center frequency" min="0.0" name="fcf"/>
				<vardef csType="k" description="Impulse response attack time in seconds" max="100.0" min="0.0" name="atk"/>
				<vardef csType="k" description="Impulse response decay time in seconds" max="100.0" min="0.0" name="dec"/>
			</input>
			<output>
				<vardef csType="a" description="Filtered audio signal" name="out"/>
			</output>
			<opcode>
				/* Formant filter */
opcode Formant, a, akkk
  ain, kfcf, katk, kdec  xin

  kfcf    limit kfcf, 0, 50000
  katk    limit katk, 0, 100
  kdec    limit kdec, 0, 100
  aout    fofilter ain, kfcf, katk, kdec

  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="MIDI activated linear ADSR envelope" name="modulators/AdsrLinMidi">
			<input>
				<vardef csType="i" description="Amplitude scale factor" name="amp"/>
				<vardef csType="i" description="Attack time in seconds" min="0.0" name="atk"/>
				<vardef csType="i" description="Decay time in seconds" min="0.0" name="dec"/>
				<vardef csType="i" description="Sustain level" max="1.0" min="0.0" name="slev"/>
				<vardef csType="i" description="Release time in seconds" min="0.0" name="rel"/>
			</input>
			<output>
				<vardef csType="k" description="Envelope at control rate" name="env"/>
			</output>
			<opcode>
				/* MIDI activated linear ADSR envelope */
opcode AdsrLinMidi, k, iiiii
  iamp, iatk, idec, islev, irel xin

  kenv     madsr      iatk, idec, islev, irel
  kenv     =          iamp*kenv

  xout kenv
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Amplify audio signal" name="amps mixers/Amp">
			<input>
				<vardef csType="a" description="Audio signal" name="in"/>
				<vardef csType="k" description="Gain" name="gain"/>
			</input>
			<output>
				<vardef csType="a" description="Amplified audio signal" name="out"/>
			</output>
			<opcode>
				/* Amplify audio signal */
opcode Amp, a, ak
  ain, kgain xin
  aout = ain * kgain
  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Analog style 8 step sequencer" name="sequencing/Sequencer">
			<input>
				<vardef csType="k" description="Trigger or clock signal" digits="0" max="1.0" min="0.0" name="step"/>
				<vardef csType="k" description="Resets to val1" digits="0" max="1.0" min="0.0" name="reset"/>
				<vardef csType="k" description="Number of steps" digits="0" max="8.0" min="1.0" name="steps"/>
				<vardef csType="k" description="Value for step 1" digits="0" max="127.0" min="0.0" name="val1"/>
				<vardef csType="k" description="Value for step 2" digits="0" max="127.0" min="0.0" name="val2"/>
				<vardef csType="k" description="Value for step 3" digits="0" max="127.0" min="0.0" name="val3"/>
				<vardef csType="k" description="Value for step 4" digits="0" max="127.0" min="0.0" name="val4"/>
				<vardef csType="k" description="Value for step 5" digits="0" max="127.0" min="0.0" name="val5"/>
				<vardef csType="k" description="Value for step 6" digits="0" max="127.0" min="0.0" name="val6"/>
				<vardef csType="k" description="Value for step 7" digits="0" max="127.0" min="0.0" name="val7"/>
				<vardef csType="k" description="Value for step 8" digits="0" max="127.0" min="0.0" name="val8"/>
			</input>
			<output>
				<vardef csType="k" description="Output value" name="out"/>
				<vardef csType="k" description="Gate signal if val is not 0" name="gate"/>
			</output>
			<opcode>
				/* Analog style 8 step sequencer */
opcode Sequencer, kk, kkkkkkkkkkk
  kstep, kreset, ksteps, kval1, kval2, kval3, kval4, kval5, kval6, kval7, kval8 xin

  kclock     init  0
  klaststep  init  0
  klastreset init  0
  kstep    limit     kstep, 0, 1
  kreset   limit     kreset, 0, 1
  ksteps   limit     ksteps, 1, 8
  ksteps   =         int(ksteps)
  kval1   limit     kval1, 0, 127
  kval1   =         int(kval1)
  kval2   limit     kval2, 0, 127
  kval2   =         int(kval2)
  kval3   limit     kval3, 0, 127
  kval3   =         int(kval3)
  kval4   limit     kval4, 0, 127
  kval4   =         int(kval4)
  kval5   limit     kval5, 0, 127
  kval5   =         int(kval5)
  kval6   limit     kval6, 0, 127
  kval6   =         int(kval6)
  kval7   limit     kval7, 0, 127
  kval7   =         int(kval7)
  kval8   limit     kval8, 0, 127
  kval8   =         int(kval8)

  if (kclock == 1) then
    kval = kval1
  elseif (kclock == 2) then
    kval = kval2
  elseif (kclock == 3) then
    kval = kval3
  elseif (kclock == 4) then
    kval = kval4
  elseif (kclock == 5) then
    kval = kval5
  elseif (kclock == 6) then
    kval = kval6
  elseif (kclock == 7) then
    kval = kval7
  elseif (kclock == 8) then
    kval = kval8
  endif
  if (klaststep == 0 &amp;&amp; kstep == 1) then
    kclock = kclock + 1
  endif

  if (kclock == ksteps+1) then
    kclock = 1
  endif

  if (kval == 0) then
    kgate = 0
  else
    kgate = 1
  endif

  if (klastreset == 0 &amp;&amp; kreset == 1) then
    kclock = 1
  endif

  klaststep = kstep
  klastreset = kreset

  xout kval, kgate
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Pulse low frequency oscillator (clock signal)" name="modulators/PulseLfo">
			<input>
				<vardef csType="k" description="Frequency of LFO" max="100.0" min="0.0" name="frq"/>
				<vardef csType="k" description="Amplitude of LFO" min="0.0" name="amp"/>
				<vardef csType="i" description="Initial phase of LFO (negativ to skip initialisation)" max="1.0" min="-0.001" name="phi"/>
			</input>
			<output>
				<vardef csType="k" description="Output of LFO" name="out"/>
			</output>
			<global>
				<def description="Pulse table">
					gipulselfo   ftgen  0, 0, 128, -7, 1, 4, 1, 0, 0, 124, 0
				</def>
			</global>
			<opcode>
				/* Pulse low frequency oscillator (clock signal) */
opcode PulseLfo, k, kki
  kfrq, kamp, iphi xin

  kfrq     limit      kfrq, 0, 100
  kamp     limit      kamp, 0, 50000
  iphi     limit      iphi, -1, 1
  kout     oscil      kamp, kfrq, gipulselfo, iphi

  xout kout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Multiply two control signals" name="maths/ControlMultiply">
			<input>
				<vardef csType="k" description="First control signal" name="in1"/>
				<vardef csType="k" description="Second control signal" name="in2"/>
			</input>
			<output>
				<vardef csType="k" description="Product of input signals" name="pro"/>
			</output>
			<opcode>
				/* Multiply two control signals */
opcode ControlMultiply, k, kk
  kin1, kin2 xin
  kpro = kin1 * kin2
  xout kpro
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Noise generator" name="sound sources/Noise">
			<input>
				<vardef csType="k" description="Amplitude of noise signal" min="0.0" name="amp"/>
			</input>
			<output>
				<vardef csType="a" description="Noise output" name="out"/>
			</output>
			<opcode>
				/* Noise generator */
opcode Noise, a, k
  kamp xin

  kamp    limit     kamp, 0, 32000
  iseed   =         rnd(1)
  aout    rand      kamp, iseed

  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Mixer for two audio signals" name="amps mixers/Mixer2">
			<input>
				<vardef csType="a" description="First audio rate signal" name="in1"/>
				<vardef csType="k" description="Amplitude multiplicator for in1" min="0.0" name="gain1"/>
				<vardef csType="a" description="Second audio rate signal" name="in2"/>
				<vardef csType="k" description="Amplitude multiplicator for in2" min="0.0" name="gain2"/>
			</input>
			<output>
				<vardef csType="a" description="Mixed input signals" name="out"/>
			</output>
			<opcode>
				/* Mixer for two audio signals */
opcode Mixer2, a, akak
  ain1, kgain1, ain2, kgain2 xin
  aout = ain1*kgain1 + ain2*kgain2
  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Mixer for four audio signals" name="amps mixers/Mixer4">
			<input>
				<vardef csType="a" description="First audio rate signal" name="in1"/>
				<vardef csType="k" description="Amplitude multiplicator for in1" min="0.0" name="gain1"/>
				<vardef csType="a" description="Second audio rate signal" name="in2"/>
				<vardef csType="k" description="Amplitude multiplicator for in2" min="0.0" name="gain2"/>
				<vardef csType="a" description="Third audio rate signal" name="in3"/>
				<vardef csType="k" description="Amplitude multiplicator for in3" min="0.0" name="gain3"/>
				<vardef csType="a" description="Fourth audio rate signal" name="in4"/>
				<vardef csType="k" description="Amplitude multiplicator for in4" min="0.0" name="gain4"/>
			</input>
			<output>
				<vardef csType="a" description="Mixed input signals" name="out"/>
			</output>
			<opcode>
				/* Mixer for four audio signals */
opcode Mixer4, a, akakakak
  ain1, kgain1, ain2, kgain2, ain3, kgain3, ain4, kgain4 xin
  aout = ain1*kgain1 + ain2*kgain2 + ain3*kgain3 + ain4*kgain4
  xout aout
endop
			</opcode>
		</moduleReference>
	</referencesModules>
	<instancesModules>
		<moduleInstance id="1" name="control/MidiNoteIn" xPos="35" yPos="48">
			<inputs>
				<val description="Scaling of MIDI velocity" id="0" value="15000.0"/>
				<val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/>
				<val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="2" name="sound sources/SawVco" xPos="190" yPos="51">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="4" name="input output/PcmMonoOut" xPos="975" yPos="50">
			<inputs>
				<val description="Audio input" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="filters/Formant" xPos="625" yPos="26">
			<inputs>
				<val description="Audio rate input" id="0" value="0.0"/>
				<val description="Filter center frequency" id="1" value="2000.0"/>
				<val description="Impulse response attack time in seconds" id="2" value="0.01"/>
				<val description="Impulse response decay time in seconds" id="3" value="0.003"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="9" name="modulators/AdsrLinMidi" xPos="846" yPos="121">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="1.0"/>
				<val description="Attack time in seconds" id="1" value="0.07"/>
				<val description="Decay time in seconds" id="2" value="0.0"/>
				<val description="Sustain level" id="3" value="1.0"/>
				<val description="Release time in seconds" id="4" value="0.06"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="11" name="amps mixers/Amp" xPos="871" yPos="49">
			<inputs>
				<val description="Audio signal" id="0" value="0.0"/>
				<val description="Gain" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="14" name="sequencing/Sequencer" xPos="123" yPos="174">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Resets to val1" id="1" value="0.0"/>
				<val description="Number of steps" id="2" value="5.0"/>
				<val description="Value for step 1" id="3" value="52.0"/>
				<val description="Value for step 2" id="4" value="53.0"/>
				<val description="Value for step 3" id="5" value="27.0"/>
				<val description="Value for step 4" id="6" value="30.0"/>
				<val description="Value for step 5" id="7" value="44.0"/>
				<val description="Value for step 6" id="8" value="0.0"/>
				<val description="Value for step 7" id="9" value="0.0"/>
				<val description="Value for step 8" id="10" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="15" name="modulators/PulseLfo" xPos="14" yPos="271">
			<inputs>
				<val description="Frequency of LFO" id="0" value="2.0"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="maths/ControlMultiply" xPos="236" yPos="172">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="10.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="sound sources/Noise" xPos="194" yPos="122">
			<inputs>
				<val description="Amplitude of noise signal" id="0" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="18" name="amps mixers/Mixer2" xPos="313" yPos="65">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="0.9"/>
				<val description="Second audio rate signal" id="2" value="0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="19" name="amps mixers/Mixer4" xPos="740" yPos="51">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="400.0"/>
				<val description="Second audio rate signal" id="2" value="0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="200.0"/>
				<val description="Third audio rate signal" id="4" value="0"/>
				<val description="Amplitude multiplicator for in3" id="5" value="150.0"/>
				<val description="Fourth audio rate signal" id="6" value="0"/>
				<val description="Amplitude multiplicator for in4" id="7" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="20" name="sequencing/Sequencer" xPos="236" yPos="238">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Resets to val1" id="1" value="0.0"/>
				<val description="Number of steps" id="2" value="5.0"/>
				<val description="Value for step 1" id="3" value="12.0"/>
				<val description="Value for step 2" id="4" value="18.0"/>
				<val description="Value for step 3" id="5" value="23.0"/>
				<val description="Value for step 4" id="6" value="9.0"/>
				<val description="Value for step 5" id="7" value="10.0"/>
				<val description="Value for step 6" id="8" value="0.0"/>
				<val description="Value for step 7" id="9" value="0.0"/>
				<val description="Value for step 8" id="10" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="21" name="maths/ControlMultiply" xPos="352" yPos="235">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="100.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="filters/Formant" xPos="627" yPos="126">
			<inputs>
				<val description="Audio rate input" id="0" value="0"/>
				<val description="Filter center frequency" id="1" value="2000.0"/>
				<val description="Impulse response attack time in seconds" id="2" value="0.01"/>
				<val description="Impulse response decay time in seconds" id="3" value="0.003"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="23" name="sequencing/Sequencer" xPos="354" yPos="298">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Resets to val1" id="1" value="0.0"/>
				<val description="Number of steps" id="2" value="5.0"/>
				<val description="Value for step 1" id="3" value="24.0"/>
				<val description="Value for step 2" id="4" value="25.0"/>
				<val description="Value for step 3" id="5" value="30.0"/>
				<val description="Value for step 4" id="6" value="22.0"/>
				<val description="Value for step 5" id="7" value="22.0"/>
				<val description="Value for step 6" id="8" value="0.0"/>
				<val description="Value for step 7" id="9" value="0.0"/>
				<val description="Value for step 8" id="10" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="24" name="maths/ControlMultiply" xPos="466" yPos="297">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="100.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="25" name="filters/Formant" xPos="625" yPos="226">
			<inputs>
				<val description="Audio rate input" id="0" value="0"/>
				<val description="Filter center frequency" id="1" value="2000.0"/>
				<val description="Impulse response attack time in seconds" id="2" value="0.01"/>
				<val description="Impulse response decay time in seconds" id="3" value="0.003"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="2" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="11" inputNum="1" outModule="9" outputNum="0"/>
		<connection inModule="14" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="16" inputNum="0" outModule="14" outputNum="0"/>
		<connection inModule="5" inputNum="1" outModule="16" outputNum="0"/>
		<connection inModule="18" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="18" inputNum="2" outModule="17" outputNum="0"/>
		<connection inModule="5" inputNum="0" outModule="18" outputNum="0"/>
		<connection inModule="4" inputNum="0" outModule="11" outputNum="0"/>
		<connection inModule="19" inputNum="0" outModule="5" outputNum="0"/>
		<connection inModule="11" inputNum="0" outModule="19" outputNum="0"/>
		<connection inModule="20" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="21" inputNum="0" outModule="20" outputNum="0"/>
		<connection inModule="22" inputNum="1" outModule="21" outputNum="0"/>
		<connection inModule="22" inputNum="0" outModule="18" outputNum="0"/>
		<connection inModule="19" inputNum="2" outModule="22" outputNum="0"/>
		<connection inModule="24" inputNum="0" outModule="23" outputNum="0"/>
		<connection inModule="25" inputNum="0" outModule="18" outputNum="0"/>
		<connection inModule="25" inputNum="1" outModule="24" outputNum="0"/>
		<connection inModule="19" inputNum="4" outModule="25" outputNum="0"/>
		<connection inModule="23" inputNum="0" outModule="15" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="23"/>
		<param name="lastModuleId" value="25"/>
	</additionalInfo>
</workspace>

