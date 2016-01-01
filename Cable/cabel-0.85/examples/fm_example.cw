<?xml version="1.0" encoding="utf-8"?>
<workspace name="fm_example">
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
		<moduleReference description="Sine oscillator (amplitude 1)" name="sound sources/SineVco">
			<input>
				<vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/>
			</input>
			<output>
				<vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/>
			</output>
			<global>
				<def description="Sine table">
					gisinevco   ftgen  0, 0, 4096, 10, 1
				</def>
			</global>
			<opcode>
				/* Sine oscillator */
opcode SineVco, a, k
  kfrq xin

  kfrq     limit      kfrq, 0, 50000
  asig     oscil      1, kfrq, gisinevco

  xout asig
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
		<moduleReference description="Add two control signals" name="maths/ControlAdd">
			<input>
				<vardef csType="k" description="First control signal" name="in1"/>
				<vardef csType="k" description="Second control signal" name="in2"/>
			</input>
			<output>
				<vardef csType="k" description="Sum of input signals" name="sum"/>
			</output>
			<opcode>
				/* Add two control signals */
opcode ControlAdd, k, kk
  kin1, kin2 xin
  ksum = kin1 + kin2
  xout ksum
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="1" name="control/MidiNoteIn" xPos="8" yPos="28">
			<inputs>
				<val description="Scaling of MIDI velocity" id="0" value="15000.0"/>
				<val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/>
				<val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="2" name="sound sources/SineVco" xPos="324" yPos="7">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="amps mixers/Amp" xPos="517" yPos="138">
			<inputs>
				<val description="Audio signal" id="0" value="0.0"/>
				<val description="Gain" id="1" value="25000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="sound sources/SineVco" xPos="515" yPos="93">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="amps mixers/Amp" xPos="437" yPos="20">
			<inputs>
				<val description="Audio signal" id="0" value="0.0"/>
				<val description="Gain" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="12" name="modulators/AdsrLinMidi" xPos="382" yPos="161">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="10000.0"/>
				<val description="Attack time in seconds" id="1" value="0.04"/>
				<val description="Decay time in seconds" id="2" value="0.5"/>
				<val description="Sustain level" id="3" value="0.9"/>
				<val description="Release time in seconds" id="4" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="maths/ControlMultiply" xPos="152" yPos="15">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="maths/ControlMultiply" xPos="175" yPos="195">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="2.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="18" name="maths/ControlMultiply" xPos="295" yPos="62">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="3.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="19" name="maths/ControlAdd" xPos="532" yPos="29">
			<inputs>
				<val description="First control signal" id="0" value="0.0"/>
				<val description="Second control signal" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="20" name="modulators/AdsrLinMidi" xPos="173" yPos="83">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="5.0"/>
				<val description="Attack time in seconds" id="1" value="0.01"/>
				<val description="Decay time in seconds" id="2" value="0.15"/>
				<val description="Sustain level" id="3" value="0.5"/>
				<val description="Release time in seconds" id="4" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="input output/PcmMonoOut" xPos="611" yPos="138">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="3" inputNum="0" outModule="5" outputNum="0"/>
		<connection inModule="3" inputNum="1" outModule="12" outputNum="0"/>
		<connection inModule="16" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="17" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="2" inputNum="0" outModule="16" outputNum="0"/>
		<connection inModule="18" inputNum="0" outModule="16" outputNum="0"/>
		<connection inModule="6" inputNum="1" outModule="18" outputNum="0"/>
		<connection inModule="6" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="19" inputNum="0" outModule="6" outputNum="0"/>
		<connection inModule="19" inputNum="1" outModule="17" outputNum="0"/>
		<connection inModule="5" inputNum="0" outModule="19" outputNum="0"/>
		<connection inModule="18" inputNum="1" outModule="20" outputNum="0"/>
		<connection inModule="22" inputNum="0" outModule="3" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="22"/>
		<param name="lastModuleId" value="22"/>
	</additionalInfo>
</workspace>

