<?xml version="1.0" encoding="utf-8"?>
<workspace name="lead_moog_midinotemonoglidein">
	<referencesModules>
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
		<moduleReference description="Get scaled value from MIDI controller" name="control/MidiCtrlIn">
			<input>
				<vardef csType="i" description="MIDI channel" digits="0" max="16.0" min="1.0" name="chnl"/>
				<vardef csType="i" description="Controller number" digits="0" max="128.0" min="1.0" name="ccnum"/>
				<vardef csType="i" description="Minimal value for scaled controller" name="min"/>
				<vardef csType="i" description="Maximal value for scaled controller" name="max"/>
			</input>
			<output>
				<vardef csType="k" description="Scaled MIDI controller value" name="out"/>
			</output>
			<opcode>
				/* Get value from MIDI controller */
opcode MidiCtrlIn, k, iiii
  ichnl, iccnum, imin, imax  xin

  kout    ctrl7       ichnl, iccnum, imin, imax
  xout kout
endop
			</opcode>
		</moduleReference>
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
		<moduleReference description="Midi note input for monosynth with portamento" name="control/MidiNoteMonoGlideIn">
			<input>
				<vardef csType="i" description="Scaling of MIDI velocity" max="32000.0" min="0.0" name="velscale"/>
				<vardef csType="i" description="Minimal value for scaled channel aftertouch" name="minafttch"/>
				<vardef csType="i" description="Maximal value for scaled channel aftertouch" name="maxafttch"/>
				<vardef csType="i" description="Portamento time in seconds" max="100.0" min="0.001" name="portatime"/>
			</input>
			<output>
				<vardef csType="k" description="Frequency of MIDI note with pitch bend information" name="frq"/>
				<vardef csType="k" description="MIDI note number of last pressed key" name="note"/>
				<vardef csType="i" description="Velocity of MIDI note" name="vel"/>
				<vardef csType="k" description="Scaled channel aftertouch" name="afttch"/>
			</output>
			<global>
				<def description="Number of instruments">
					gkcntmidinotemonoglidein init 0
				</def>
				<def description="Old pitch of instruments">
					giptchmidinotemonoglidein init 200
				</def>
			</global>
			<opcode>
				/* Midi note input for monosynth with portamento */
opcode MidiNoteMonoGlideIn, kkik, iiii

  icnt                =    i(gkcntmidinotemonoglidein)+1
  gkcntmidinotemonoglidein init icnt

  /* Turn instrument off if there's a new instance */
  if (icnt &lt; gkcntmidinotemonoglidein) then
    turnoff     
  endif

  ivelscale, iminafttch, imaxafttch, iportatime xin

  knote init 0
  kvel init 0
  kafttch init 0
  kptchbnd init 0

  midinoteonkey knote, kvel
  midichannelaftertouch kafttch, iminafttch, imaxafttch
  midipitchbend kptchbnd
  ifrq cpsmidi
  ivel ampmidi  ivelscale

  /* Add portamento to frequency */
  kglide expseg giptchmidinotemonoglidein, iportatime, ifrq, 1, ifrq
  giptchmidinotemonoglidein = ifrq
  kfrq = kglide

  /* Add pitchbend (-1 octave to +1 octave) */
  kfrq = kfrq * 2^kptchbnd

  xout kfrq, knote, ivel, kafttch
endop
			</opcode>
		</moduleReference>
	</referencesModules>
	<instancesModules>
		<moduleInstance id="2" name="maths/ControlMultiply" xPos="419" yPos="83">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="2.01"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="maths/ControlMultiply" xPos="419" yPos="143">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="4.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="4" name="sound sources/SawVco" xPos="554" yPos="23">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="sound sources/SawVco" xPos="553" yPos="82">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="sound sources/SawVco" xPos="554" yPos="143">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.122"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="7" name="amps mixers/Mixer4" xPos="665" yPos="59">
			<inputs>
				<val description="First audio rate signal" id="0" value="0.0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="0.89"/>
				<val description="Second audio rate signal" id="2" value="0.0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="1.0"/>
				<val description="Third audio rate signal" id="4" value="0.0"/>
				<val description="Amplitude multiplicator for in3" id="5" value="1.0"/>
				<val description="Fourth audio rate signal" id="6" value="0.0"/>
				<val description="Amplitude multiplicator for in4" id="7" value="0.4"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="8" name="amps mixers/Amp" xPos="771" yPos="69">
			<inputs>
				<val description="Audio signal" id="0" value="0.0"/>
				<val description="Gain" id="1" value="0.4"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="9" name="filters/MoogVcf" xPos="872" yPos="75">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0.0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="11" name="modulators/AdsrLinMidi" xPos="840" yPos="158">
			<inputs>
				<val description="Amplitude scale factor" id="0" value="20000.0"/>
				<val description="Attack time in seconds" id="1" value="0.02"/>
				<val description="Decay time in seconds" id="2" value="0.0"/>
				<val description="Sustain level" id="3" value="1.0"/>
				<val description="Release time in seconds" id="4" value="0.08"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="12" name="amps mixers/Amp" xPos="967" yPos="105">
			<inputs>
				<val description="Audio signal" id="0" value="0.0"/>
				<val description="Gain" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="14" name="input output/PcmMonoOut" xPos="964" yPos="177">
			<inputs>
				<val description="Audio input" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="15" name="control/MidiCtrlIn" xPos="556" yPos="279">
			<inputs>
				<val description="MIDI channel" id="0" value="1.0"/>
				<val description="Controller number" id="1" value="1.0"/>
				<val description="Minimal value for scaled controller" id="2" value="110.0"/>
				<val description="Maximal value for scaled controller" id="3" value="25.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="sound sources/SquareVco" xPos="549" yPos="202">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Pulse width of square wave" id="1" value="0.468"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="maths/ControlMultiply" xPos="406" yPos="202">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="20" name="maths/ControlMultiply" xPos="681" yPos="264">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="21" name="control/MidiCtrlIn" xPos="43" yPos="314">
			<inputs>
				<val description="MIDI channel" id="0" value="1.0"/>
				<val description="Controller number" id="1" value="2.0"/>
				<val description="Minimal value for scaled controller" id="2" value="0.0"/>
				<val description="Maximal value for scaled controller" id="3" value="0.23"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="modulators/SineLfo" xPos="131" yPos="167">
			<inputs>
				<val description="Frequency of LFO" id="0" value="6.5"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="23" name="maths/ControlMultiply" xPos="238" yPos="126">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="24" name="maths/ControlAdd" xPos="295" yPos="50">
			<inputs>
				<val description="First control signal" id="0" value="0.0"/>
				<val description="Second control signal" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="25" name="control/MidiNoteMonoGlideIn" xPos="14" yPos="51">
			<inputs>
				<val description="Scaling of MIDI velocity" id="0" value="15000.0"/>
				<val description="Minimal value for scaled channel aftertouch" id="1" value="0.0"/>
				<val description="Maximal value for scaled channel aftertouch" id="2" value="127.0"/>
				<val description="Portamento time in seconds" id="3" value="0.05"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="26" name="maths/ControlMultiply" xPos="97" yPos="244">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="5" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="6" inputNum="0" outModule="3" outputNum="0"/>
		<connection inModule="7" inputNum="0" outModule="4" outputNum="0"/>
		<connection inModule="7" inputNum="2" outModule="5" outputNum="0"/>
		<connection inModule="7" inputNum="4" outModule="6" outputNum="0"/>
		<connection inModule="8" inputNum="0" outModule="7" outputNum="0"/>
		<connection inModule="9" inputNum="0" outModule="8" outputNum="0"/>
		<connection inModule="12" inputNum="0" outModule="9" outputNum="0"/>
		<connection inModule="12" inputNum="1" outModule="11" outputNum="0"/>
		<connection inModule="16" inputNum="0" outModule="17" outputNum="0"/>
		<connection inModule="7" inputNum="6" outModule="16" outputNum="0"/>
		<connection inModule="20" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="20" inputNum="1" outModule="15" outputNum="0"/>
		<connection inModule="9" inputNum="1" outModule="20" outputNum="0"/>
		<connection inModule="14" inputNum="0" outModule="12" outputNum="0"/>
		<connection inModule="24" inputNum="1" outModule="23" outputNum="0"/>
		<connection inModule="23" inputNum="1" outModule="22" outputNum="0"/>
		<connection inModule="17" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="3" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="2" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="4" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="24" inputNum="0" outModule="25" outputNum="0"/>
		<connection inModule="23" inputNum="0" outModule="25" outputNum="0"/>
		<connection inModule="26" inputNum="1" outModule="21" outputNum="0"/>
		<connection inModule="26" inputNum="0" outModule="21" outputNum="0"/>
		<connection inModule="22" inputNum="1" outModule="26" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="21"/>
		<param name="lastModuleId" value="26"/>
	</additionalInfo>
</workspace>

