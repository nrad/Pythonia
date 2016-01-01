<?xml version="1.0" encoding="utf-8"?>
<workspace name="sweep_strings">
	<referencesModules>
		<moduleReference description="Square oscillator (amplitude 1)" name="sound sources/SquareVco">
			<input>
				<vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/>
				<vardef csType="k" description="Pulse width of square wave" max="0.999" min="0.001" name="pw"/>
			</input>
			<output>
				<vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/>
			</output>
			<opcode>
				/* Square oscillator */
opcode SquareVco, a, kk
  kfrq, kpw xin

  kfrq     limit     kfrq, 0, 50000
  kpw      limit     kpw, 0.001, 0.999
  aout     vco2      1, kfrq, 2, kpw

  xout aout
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Sine low frequency oscillator" name="modulators/SineLfo">
			<input>
				<vardef csType="k" description="Frequency of LFO" max="100.0" min="0.0" name="frq"/>
				<vardef csType="k" description="Amplitude of LFO" min="0.0" name="amp"/>
				<vardef csType="i" description="Initial phase of LFO (negativ to skip initialisation)" max="1.0" min="-0.001" name="phi"/>
			</input>
			<output>
				<vardef csType="k" description="Output of LFO" name="out"/>
			</output>
			<global>
				<def description="Sine table">
					gisinelfo   ftgen  0, 0, 2048, 10 ,1
				</def>
			</global>
			<opcode>
				/* Sine low frequency oscillator */
opcode SineLfo, k, kki
  kfrq, kamp, iphi xin

  kfrq     limit      kfrq, 0, 100
  kamp     limit      kamp, 0, 50000
  iphi     limit      iphi, -1, 1
  kout     oscil      kamp, kfrq, gisinelfo, iphi

  xout kout
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
		<moduleReference description="Moog lowpass filter, to avoid clipping use input signal with max amplitude 1" name="filters/MoogVcf">
			<input>
				<vardef csType="a" description="Audio rate input, to avoid clipping use input signal with max amplitude 1" max="1.0" min="-1.0" name="in"/>
				<vardef csType="k" description="Filter cut-off frequency" min="0.0" name="fco"/>
				<vardef csType="k" description="Filter resonance (self-resonates at 1)" max="2.0" min="0.0" name="res"/>
			</input>
			<output>
				<vardef csType="a" description="Filtered audio signal" name="out"/>
			</output>
			<opcode>
				/* Moog lowpass filter */
opcode MoogVcf, a, akk
  ain, kfco, kres  xin

  ain     limit ain, -1, 1
  kfco    limit kfco, 0, 50000
  kres    limit kres, 0, 2
  aout    moogvcf ain, kfco, kres

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
		<moduleReference description="Reverb based on the MN3011 IC" name="effects/AnalogEcho">
			<input>
				<vardef csType="a" description="Audio input" name="in"/>
				<vardef csType="i" description="Output level" max="1.0" min="0.0" name="lvl"/>
				<vardef csType="i" description="Delay factor" max="1.0" min="0.0" name="delay"/>
				<vardef csType="i" description="Feedback amount" max="1.0" min="0.0" name="fdbk"/>
				<vardef csType="i" description="Reverb amount" max="1.0" min="0.0" name="echo"/>
			</input>
			<output>
				<vardef csType="a" description="Input with applied echo" name="out"/>
			</output>
			<opcode>
				/* Reverb based on the MN3011 IC */
opcode AnalogEcho, a, aiiii
  ain, ilvl, idelay, ifdbk, iecho  xin

  afdbk     init     0
  ain       =        ain+afdbk*ifdbk
  atemp     delayr   1
  atap1     deltapi  0.0396*idelay
  atap2     deltapi  0.0662*idelay
  atap3     deltapi  0.1194*idelay
  atap4     deltapi  0.1726*idelay
  atap5     deltapi  0.2790*idelay
  atap6     deltapi  0.3328*idelay
            delayw   ain
  afdbk     butterlp atap6, 7000
  abbd      sum      atap1, atap2, atap3, atap4, atap5, atap6
  abbd      butterlp abbd, 7000
  aout      =        (ain+abbd*iecho)*ilvl

  ; stay triggered until echo fades out
  kfade     linsegr  1, 0.01, 1, 0.33*idelay*(1+ifdbk)*(1+iecho), 0
  aout      =        aout*kfade
  xout aout
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="1" name="sound sources/SquareVco" xPos="617" yPos="130">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0"/>
				<val description="Pulse width of square wave" id="1" value="0.572"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="sound sources/SquareVco" xPos="618" yPos="52">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0"/>
				<val description="Pulse width of square wave" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="4" name="modulators/SineLfo" xPos="362" yPos="27">
			<inputs>
				<val description="Frequency of LFO" id="0" value="1.2"/>
				<val description="Amplitude of LFO" id="1" value="0.33"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="maths/ControlAdd" xPos="481" yPos="42">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="maths/ControlMultiply" xPos="470" yPos="132">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="1.011"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="8" name="sound sources/SquareVco" xPos="614" yPos="203">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0"/>
				<val description="Pulse width of square wave" id="1" value="0.46"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="9" name="maths/ControlMultiply" xPos="468" yPos="200">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="10" name="amps mixers/Mixer4" xPos="749" yPos="68">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="0.32"/>
				<val description="Second audio rate signal" id="2" value="0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="0.32"/>
				<val description="Third audio rate signal" id="4" value="0"/>
				<val description="Amplitude multiplicator for in3" id="5" value="0.0"/>
				<val description="Fourth audio rate signal" id="6" value="0"/>
				<val description="Amplitude multiplicator for in4" id="7" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="13" name="input output/PcmMonoOut" xPos="792" yPos="431">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="14" name="control/MidiNoteIn" xPos="13" yPos="192">
			<inputs>
				<val description="Scaling of MIDI velocity" id="0" value="14000.0"/>
				<val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/>
				<val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="15" name="filters/MoogVcf" xPos="762" yPos="252">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="modulators/SineLfo" xPos="519" yPos="286">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.1"/>
				<val description="Amplitude of LFO" id="1" value="1100.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="maths/ControlAdd" xPos="619" yPos="284">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="2300.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="19" name="modulators/AdsrLinMidi" xPos="506" yPos="375">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="1.0"/>
				<val description="Attack time in seconds" id="1" value="0.1"/>
				<val description="Decay time in seconds" id="2" value="1.0"/>
				<val description="Sustain level" id="3" value="0.8"/>
				<val description="Release time in seconds" id="4" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="modulators/AdsrLinMidi" xPos="26" yPos="34">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="0.017"/>
				<val description="Attack time in seconds" id="1" value="5.0"/>
				<val description="Decay time in seconds" id="2" value="0"/>
				<val description="Sustain level" id="3" value="1.0"/>
				<val description="Release time in seconds" id="4" value="0.2"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="23" name="modulators/SineLfo" xPos="173" yPos="45">
			<inputs>
				<val description="Frequency of LFO" id="0" value="4.5"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="24" name="maths/ControlAdd" xPos="335" yPos="145">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="25" name="maths/ControlMultiply" xPos="181" yPos="130">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="28" name="effects/AnalogEcho" xPos="666" yPos="429">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
				<val description="Output level" id="1" value="1.0"/>
				<val description="Delay factor" id="2" value="0.919"/>
				<val description="Feedback amount" id="3" value="0.363"/>
				<val description="Reverb amount" id="4" value="0.315"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="29" name="amps mixers/Amp" xPos="757" yPos="343">
			<inputs>
				<val description="Audio signal" id="0" value="0"/>
				<val description="Gain" id="1" value="0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="5" inputNum="0" outModule="4" outputNum="0"/>
		<connection inModule="3" inputNum="1" outModule="5" outputNum="0"/>
		<connection inModule="1" inputNum="0" outModule="6" outputNum="0"/>
		<connection inModule="8" inputNum="0" outModule="9" outputNum="0"/>
		<connection inModule="10" inputNum="0" outModule="3" outputNum="0"/>
		<connection inModule="10" inputNum="2" outModule="1" outputNum="0"/>
		<connection inModule="10" inputNum="6" outModule="8" outputNum="0"/>
		<connection inModule="15" inputNum="0" outModule="10" outputNum="0"/>
		<connection inModule="17" inputNum="0" outModule="16" outputNum="0"/>
		<connection inModule="23" inputNum="1" outModule="22" outputNum="0"/>
		<connection inModule="24" inputNum="0" outModule="25" outputNum="0"/>
		<connection inModule="24" inputNum="1" outModule="14" outputNum="0"/>
		<connection inModule="6" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="13" inputNum="0" outModule="28" outputNum="0"/>
		<connection inModule="9" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="3" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="29" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="29" inputNum="1" outModule="19" outputNum="0"/>
		<connection inModule="28" inputNum="0" outModule="29" outputNum="0"/>
		<connection inModule="15" inputNum="1" outModule="17" outputNum="0"/>
		<connection inModule="25" inputNum="1" outModule="14" outputNum="0"/>
		<connection inModule="25" inputNum="0" outModule="23" outputNum="0"/>
		<connection inModule="19" inputNum="0" outModule="14" outputNum="2"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="14"/>
		<param name="lastModuleId" value="33"/>
	</additionalInfo>
</workspace>

