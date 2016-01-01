<?xml version="1.0" encoding="utf-8"?>
<workspace name="space_flight">
	<referencesModules>
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
		<moduleReference description="Triggered linear ADSR envelope" name="modulators/AdsrLinTrigger">
			<input>
				<vardef csType="k" description="Trigger or clock signal" digits="0" max="1.0" min="0.0" name="trigger"/>
				<vardef csType="i" description="Amplitude scale factor" name="amp"/>
				<vardef csType="i" description="Attack time in seconds" max="1000.0" min="0.0" name="atk"/>
				<vardef csType="i" description="Decay time in seconds" max="1000.0" min="0.0" name="dec"/>
				<vardef csType="i" description="Sustain level" max="1.0" min="0.0" name="slev"/>
				<vardef csType="i" description="Sustain time in seconds" max="1000.0" min="0.0" name="stime"/>
				<vardef csType="i" description="Release time in seconds" max="1000.0" min="0.0" name="rel"/>
			</input>
			<output>
				<vardef csType="k" description="Envelope control signal" name="env"/>
			</output>
			<opcode>
				/* Triggered linear ADSR envelope */
opcode AdsrLinTrigger, k, kiiiiii
  ktrigger, iamp, iatk, idec, islev, istime, irel xin
  ktrigger limit ktrigger, 0, 1
  klasttrigger init 0

  if (klasttrigger == 0 &amp;&amp; ktrigger == 1) then
    kstart = 1
  else
    kstart = 0
  endif
reset:
  if (kstart &lt; 1) goto contin
  reinit reset

contin:
  kenv linseg 0, iatk, 1, idec, islev, istime, islev, irel, 0
  rireturn

  kenv = iamp*kenv
  klasttrigger = ktrigger
  xout kenv
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
		<moduleReference description="Triangle low frequency oscillator" name="modulators/TriangleLfo">
			<input>
				<vardef csType="k" description="Frequency of LFO" max="100.0" min="0.0" name="frq"/>
				<vardef csType="k" description="Amplitude of LFO" min="0.0" name="amp"/>
				<vardef csType="i" description="Initial phase of LFO (negativ to skip initialisation)" max="1.0" min="-0.001" name="phi"/>
			</input>
			<output>
				<vardef csType="k" description="Output of LFO" name="out"/>
			</output>
			<global>
				<def description="Triangle table">
					gitrianglelfo   ftgen  0, 0, 2048, 7, 1, 1024, -1, 1024, 1
				</def>
			</global>
			<opcode>
				/* Triangle low frequency oscillator */
opcode TriangleLfo, k, kki
  kfrq, kamp, iphi xin

  kfrq     limit      kfrq, 0, 100
  kamp     limit      kamp, 0, 50000
  iphi     limit      iphi, -1, 1
  kout     oscil      kamp, kfrq, gitrianglelfo, iphi

  xout kout
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="2" name="filters/MoogVcf" xPos="320" yPos="7">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="1.226"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="modulators/PulseLfo" xPos="173" yPos="121">
			<inputs>
				<val description="Frequency of LFO" id="0" value="13.0"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="modulators/AdsrLinTrigger" xPos="284" yPos="107">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Amplitude scale factor" id="1" value="8000.0"/>
				<val description="Attack time in seconds" id="2" value="0.008"/>
				<val description="Decay time in seconds" id="3" value="0.02"/>
				<val description="Sustain level" id="4" value="0.1"/>
				<val description="Sustain time in seconds" id="5" value="0.001"/>
				<val description="Release time in seconds" id="6" value="0.07"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="maths/ControlAdd" xPos="132" yPos="61">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="5000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="8" name="modulators/TriangleLfo" xPos="19" yPos="62">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.1"/>
				<val description="Amplitude of LFO" id="1" value="1276.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="9" name="input output/PcmMonoOut" xPos="819" yPos="367">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="12" name="sound sources/SquareVco" xPos="261" yPos="280">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="55.0"/>
				<val description="Pulse width of square wave" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="13" name="modulators/TriangleLfo" xPos="15" yPos="280">
			<inputs>
				<val description="Frequency of LFO" id="0" value="1.0"/>
				<val description="Amplitude of LFO" id="1" value="0.25"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="14" name="maths/ControlAdd" xPos="136" yPos="282">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="15" name="filters/MoogVcf" xPos="461" yPos="288">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.387"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="filters/MoogVcf" xPos="462" yPos="367">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.419"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="filters/MoogVcf" xPos="461" yPos="449">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.403"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="18" name="maths/ControlAdd" xPos="255" yPos="358">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="85.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="19" name="maths/ControlAdd" xPos="259" yPos="440">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="85.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="20" name="maths/ControlAdd" xPos="254" yPos="515">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="80.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="21" name="modulators/TriangleLfo" xPos="135" yPos="359">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.8"/>
				<val description="Amplitude of LFO" id="1" value="8.5"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="modulators/TriangleLfo" xPos="134" yPos="437">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.5"/>
				<val description="Amplitude of LFO" id="1" value="12.75"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="23" name="modulators/TriangleLfo" xPos="133" yPos="514">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.3"/>
				<val description="Amplitude of LFO" id="1" value="12.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="24" name="amps mixers/Mixer4" xPos="573" yPos="325">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="1.0"/>
				<val description="Second audio rate signal" id="2" value="0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="1.0"/>
				<val description="Third audio rate signal" id="4" value="0"/>
				<val description="Amplitude multiplicator for in3" id="5" value="1.0"/>
				<val description="Fourth audio rate signal" id="6" value="0"/>
				<val description="Amplitude multiplicator for in4" id="7" value="0.004"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="25" name="effects/AnalogEcho" xPos="798" yPos="239">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
				<val description="Output level" id="1" value="1.0"/>
				<val description="Delay factor" id="2" value="0.887"/>
				<val description="Feedback amount" id="3" value="0.282"/>
				<val description="Reverb amount" id="4" value="0.347"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="27" name="amps mixers/Mixer2" xPos="681" yPos="242">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="1.0"/>
				<val description="Second audio rate signal" id="2" value="0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="10000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="30" name="sound sources/Noise" xPos="209" yPos="10">
			<inputs>
				<val description="Amplitude of noise signal" id="0" value="0.01"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="31" name="filters/Formant" xPos="420" yPos="558">
			<inputs>
				<val description="Audio rate input" id="0" value="0"/>
				<val description="Filter center frequency" id="1" value="2000.0"/>
				<val description="Impulse response attack time in seconds" id="2" value="0.01"/>
				<val description="Impulse response decay time in seconds" id="3" value="0.003"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="32" name="sound sources/SawVco" xPos="266" yPos="584">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="220.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.275"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="33" name="maths/ControlAdd" xPos="262" yPos="643">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="800.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="34" name="modulators/TriangleLfo" xPos="133" yPos="617">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.07"/>
				<val description="Amplitude of LFO" id="1" value="600.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="6" inputNum="0" outModule="8" outputNum="0"/>
		<connection inModule="2" inputNum="1" outModule="6" outputNum="0"/>
		<connection inModule="5" inputNum="0" outModule="3" outputNum="0"/>
		<connection inModule="14" inputNum="0" outModule="13" outputNum="0"/>
		<connection inModule="12" inputNum="1" outModule="14" outputNum="0"/>
		<connection inModule="15" inputNum="0" outModule="12" outputNum="0"/>
		<connection inModule="16" inputNum="0" outModule="12" outputNum="0"/>
		<connection inModule="17" inputNum="0" outModule="12" outputNum="0"/>
		<connection inModule="16" inputNum="1" outModule="19" outputNum="0"/>
		<connection inModule="17" inputNum="1" outModule="20" outputNum="0"/>
		<connection inModule="18" inputNum="0" outModule="21" outputNum="0"/>
		<connection inModule="19" inputNum="0" outModule="22" outputNum="0"/>
		<connection inModule="20" inputNum="0" outModule="23" outputNum="0"/>
		<connection inModule="24" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="24" inputNum="2" outModule="16" outputNum="0"/>
		<connection inModule="24" inputNum="4" outModule="17" outputNum="0"/>
		<connection inModule="9" inputNum="0" outModule="25" outputNum="0"/>
		<connection inModule="27" inputNum="1" outModule="5" outputNum="0"/>
		<connection inModule="27" inputNum="2" outModule="24" outputNum="0"/>
		<connection inModule="25" inputNum="0" outModule="27" outputNum="0"/>
		<connection inModule="27" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="15" inputNum="1" outModule="18" outputNum="0"/>
		<connection inModule="2" inputNum="0" outModule="30" outputNum="0"/>
		<connection inModule="24" inputNum="6" outModule="31" outputNum="0"/>
		<connection inModule="31" inputNum="0" outModule="32" outputNum="0"/>
		<connection inModule="31" inputNum="1" outModule="33" outputNum="0"/>
		<connection inModule="33" inputNum="0" outModule="34" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="15"/>
		<param name="lastModuleId" value="34"/>
	</additionalInfo>
</workspace>

