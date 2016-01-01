<?xml version="1.0" encoding="utf-8"?>
<workspace name="sequencer_notequantizer_sampleandhold">
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
		<moduleReference description="A second-order low-pass Butterworth filter" name="filters/ButterLp">
			<input>
				<vardef csType="a" description="Audio rate input" name="in"/>
				<vardef csType="k" description="Filter cut-off frequency" min="0.0" name="fco"/>
			</input>
			<output>
				<vardef csType="a" description="Filtered audio signal" name="out"/>
			</output>
			<opcode>
				/* Second-order Butterworth low-pass filter */
opcode ButterLp, a, ak
  ain, kfco  xin

  kfco    limit kfco, 0, 50000
  aout    butterlp ain, kfco

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
		<moduleReference description="Convert MIDI note number into frequency" name="maths/Midi2Frq">
			<input>
				<vardef csType="k" description="MIDI note number" max="127.0" min="0.0" name="in"/>
			</input>
			<output>
				<vardef csType="k" description="Corresponding frequency" name="out"/>
			</output>
			<opcode>
				/* Convert MIDI note number into frequency */
opcode Midi2Frq, k, k
  kin xin
  kin limit kin, 0 ,127
  kin =     int(kin)

  kout = 440.0/32 * 2^((kin - 9)/12.0)

  xout kout
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
		<moduleReference description="Sample and hold input signal at trigger frequency" name="modulators/SampleAndHold">
			<input>
				<vardef csType="k" description="Trigger signal (1 sample, 0 hold sample)" digits="0" max="1.0" min="0.0" name="trigger"/>
				<vardef csType="k" description="Input signal" name="in"/>
			</input>
			<output>
				<vardef csType="k" description="Output of Sample and Hold" name="out"/>
			</output>
			<opcode>
				/* Sample and Hold */
opcode SampleAndHold, k, kk
  ktrigger, kin xin

  klasttrigger init 0
  khold        init 0
  ktrigger limit     ktrigger, 0, 1

  if (klasttrigger == 0 &amp;&amp; ktrigger == 1) then
     khold = 1
  else
     khold = 0
  endif
  klasttrigger = ktrigger
  kout     samphold  kin, khold

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
		<moduleReference description="Quantize the incoming midi note numbers to selected pitches" name="control/NoteQuantizer">
			<input>
				<vardef csType="k" description="Input signal" name="in"/>
				<vardef csType="k" description="Select c" digits="0" max="1.0" min="0.0" name="c"/>
				<vardef csType="k" description="Select cis" digits="0" max="1.0" min="0.0" name="cis"/>
				<vardef csType="k" description="Select d" digits="0" max="1.0" min="0.0" name="d"/>
				<vardef csType="k" description="Select dis" digits="0" max="1.0" min="0.0" name="dis"/>
				<vardef csType="k" description="Select e" digits="0" max="1.0" min="0.0" name="e"/>
				<vardef csType="k" description="Select f" digits="0" max="1.0" min="0.0" name="f"/>
				<vardef csType="k" description="Select fis" digits="0" max="1.0" min="0.0" name="fis"/>
				<vardef csType="k" description="Select g" digits="0" max="1.0" min="0.0" name="g"/>
				<vardef csType="k" description="Select gis" digits="0" max="1.0" min="0.0" name="gis"/>
				<vardef csType="k" description="Select a" digits="0" max="1.0" min="0.0" name="a"/>
				<vardef csType="k" description="Select ais" digits="0" max="1.0" min="0.0" name="ais"/>
				<vardef csType="k" description="Select b" digits="0" max="1.0" min="0.0" name="b"/>
			</input>
			<output>
				<vardef csType="k" description="Quantized input signal" name="out"/>
			</output>
			<opcode>
				/* Quantize  the incoming midi note numbers to selected pitches */
opcode NoteQuantizer, k, kkkkkkkkkkkkk
  kin, kc, kcis, kd, kdis, ke, kf, kfis, kg, kgis, ka, kais, kb xin

  kin     limit    kin, 0, 127
  kin     =        int(kin)

  kc      limit    kc, 0, 1
  kc      =        int(kc)
  kcis    limit    kcis, 0, 1
  kcis    =        int(kcis)
  kd      limit    kd, 0, 1
  kd      =        int(kd)
  kdis    limit    kdis, 0, 1
  kdis    =        int(kdis)
  ke      limit    ke, 0, 1
  ke      =        int(ke)
  kf      limit    kf, 0, 1
  kf      =        int(kf)
  kfis    limit    kfis, 0, 1
  kfis    =        int(kfis)
  kg      limit    kg, 0, 1
  kg      =        int(kg)
  kgis    limit    kgis, 0, 1
  kgis    =        int(kgis)
  ka      limit    ka, 0, 1
  ka      =        int(ka)
  kais    limit    kais, 0, 1
  kais    =        int(kais)
  kb      limit    kb, 0, 1
  kb      =        int(kb)

  kout    init     0
  knote   =        kin%12
  kset    =        0

  kskip   = kc+kcis+kd+kdis+ke+kf+kfis+kg+kgis+ka+kais+kb
  if (kskip == 0) goto skip

restart:
  if (knote == 0 &amp;&amp; kc == 1) then
    kout = kin
    kset = 1
  elseif (knote == 1 &amp;&amp; kcis == 1) then
    kout = kin
    kset = 1
  elseif (knote == 2 &amp;&amp; kd == 1) then
    kout = kin
    kset = 1
  elseif (knote == 3 &amp;&amp; kdis == 1) then
    kout = kin
    kset = 1
  elseif (knote == 4 &amp;&amp; ke == 1) then
    kout = kin
    kset = 1
  elseif (knote == 5 &amp;&amp; kf == 1) then
    kout = kin
    kset = 1
  elseif (knote == 6 &amp;&amp; kfis == 1) then
    kout = kin
    kset = 1
  elseif (knote == 7 &amp;&amp; kg == 1) then
    kout = kin
    kset = 1
  elseif (knote == 8 &amp;&amp; kgis == 1) then
    kout = kin
    kset = 1
  elseif (knote == 9 &amp;&amp; ka == 1) then
    kout = kin
    kset = 1
  elseif (knote == 10 &amp;&amp; kais == 1) then
    kout = kin
    kset = 1
  elseif (knote == 11 &amp;&amp; kb == 1) then
    kout = kin
    kset = 1
  endif
  kin = kin + 1
  knote = kin%12
  if (kset == 0) goto restart

skip:
  xout kout
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
		<moduleReference description="Delay an input signal" name="effects/Delay">
			<input>
				<vardef csType="a" description="Audio input" name="in"/>
				<vardef csType="i" description="Delay time in seconds" max="10.0" min="0.001" name="time"/>
			</input>
			<output>
				<vardef csType="a" description="Delayed input signal" name="out"/>
			</output>
			<opcode>
				/* Delay an input signal */
opcode Delay, a, ai
  ain, itime  xin

  itime  limit  itime, 0, 10
  aout   delay  ain, itime

  ; stay triggerd until delay is nearly finished
  kfade  linsegr 0, 0.01, 0, itime, 0
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="2" name="sound sources/SquareVco" xPos="809" yPos="8">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Pulse width of square wave" id="1" value="0.387"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="filters/ButterLp" xPos="1070" yPos="51">
			<inputs>
				<val description="Audio rate input" id="0" value="0.0"/>
				<val description="Filter cut-off frequency" id="1" value="2000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="input output/PcmMonoOut" xPos="1142" yPos="280">
			<inputs>
				<val description="Audio input" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="11" name="maths/ControlMultiply" xPos="709" yPos="67">
			<inputs>
				<val description="First control signal" id="0" value="1.0"/>
				<val description="Second control signal" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="12" name="sound sources/SquareVco" xPos="856" yPos="66">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Pulse width of square wave" id="1" value="0.516"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="13" name="amps mixers/Mixer2" xPos="972" yPos="10">
			<inputs>
				<val description="First audio rate signal" id="0" value="0.0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="0.7"/>
				<val description="Second audio rate signal" id="2" value="0.0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="0.4"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="15" name="sequencing/Sequencer" xPos="233" yPos="8">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Resets to val1" id="1" value="0.0"/>
				<val description="Number of steps" id="2" value="8.0"/>
				<val description="Value for step 1" id="3" value="36.0"/>
				<val description="Value for step 2" id="4" value="38.0"/>
				<val description="Value for step 3" id="5" value="50.0"/>
				<val description="Value for step 4" id="6" value="36.0"/>
				<val description="Value for step 5" id="7" value="38.0"/>
				<val description="Value for step 6" id="8" value="50.0"/>
				<val description="Value for step 7" id="9" value="38.0"/>
				<val description="Value for step 8" id="10" value="50.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="16" name="maths/Midi2Frq" xPos="616" yPos="16">
			<inputs>
				<val description="MIDI note number" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="17" name="modulators/PulseLfo" xPos="14" yPos="27">
			<inputs>
				<val description="Frequency of LFO" id="0" value="5.0"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="18" name="modulators/AdsrLinTrigger" xPos="833" yPos="132">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Amplitude scale factor" id="1" value="4000.0"/>
				<val description="Attack time in seconds" id="2" value="0.01"/>
				<val description="Decay time in seconds" id="3" value="0.2"/>
				<val description="Sustain level" id="4" value="0.0"/>
				<val description="Sustain time in seconds" id="5" value="3.0"/>
				<val description="Release time in seconds" id="6" value="0.01"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="19" name="modulators/AdsrLinTrigger" xPos="987" yPos="181">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Amplitude scale factor" id="1" value="10000.0"/>
				<val description="Attack time in seconds" id="2" value="0.01"/>
				<val description="Decay time in seconds" id="3" value="0.0"/>
				<val description="Sustain level" id="4" value="1.0"/>
				<val description="Sustain time in seconds" id="5" value="0.17"/>
				<val description="Release time in seconds" id="6" value="0.01"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="20" name="sound sources/Noise" xPos="9" yPos="441">
			<inputs>
				<val description="Amplitude of noise signal" id="0" value="15.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="21" name="modulators/SampleAndHold" xPos="119" yPos="398">
			<inputs>
				<val description="Trigger signal (1 sample, 0 hold sample)" id="0" value="1.0"/>
				<val description="Input signal" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="22" name="modulators/PulseLfo" xPos="11" yPos="366">
			<inputs>
				<val description="Frequency of LFO" id="0" value="10.0"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="24" name="maths/ControlAdd" xPos="268" yPos="396">
			<inputs>
				<val description="First control signal" id="0" value="0.0"/>
				<val description="Second control signal" id="1" value="60.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="25" name="control/NoteQuantizer" xPos="394" yPos="306">
			<inputs>
				<val description="Input signal" id="0" value="0.0"/>
				<val description="Select c" id="1" value="0.0"/>
				<val description="Select cis" id="2" value="0.0"/>
				<val description="Select d" id="3" value="1.0"/>
				<val description="Select dis" id="4" value="0.0"/>
				<val description="Select e" id="5" value="0.0"/>
				<val description="Select f" id="6" value="1.0"/>
				<val description="Select fis" id="7" value="0.0"/>
				<val description="Select g" id="8" value="1.0"/>
				<val description="Select gis" id="9" value="0.0"/>
				<val description="Select a" id="10" value="1.0"/>
				<val description="Select ais" id="11" value="0.0"/>
				<val description="Select b" id="12" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="26" name="maths/Midi2Frq" xPos="534" yPos="309">
			<inputs>
				<val description="MIDI note number" id="0" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="27" name="sound sources/SawVco" xPos="642" yPos="310">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0.0"/>
				<val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="28" name="filters/MoogVcf" xPos="754" yPos="305">
			<inputs>
				<val description="Audio rate input, to avoid clipping use input signal with max amplitude 1" id="0" value="0.0"/>
				<val description="Filter cut-off frequency" id="1" value="15590.75"/>
				<val description="Filter resonance (self-resonates at 1)" id="2" value="0.452"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="29" name="amps mixers/Mixer2" xPos="1159" yPos="173">
			<inputs>
				<val description="First audio rate signal" id="0" value="0.0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="1.0"/>
				<val description="Second audio rate signal" id="2" value="0.0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="30" name="modulators/AdsrLinTrigger" xPos="715" yPos="384">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Amplitude scale factor" id="1" value="13000.0"/>
				<val description="Attack time in seconds" id="2" value="0.01"/>
				<val description="Decay time in seconds" id="3" value="0.02"/>
				<val description="Sustain level" id="4" value="0.8"/>
				<val description="Sustain time in seconds" id="5" value="0.05"/>
				<val description="Release time in seconds" id="6" value="0.02"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="31" name="modulators/AdsrLinTrigger" xPos="541" yPos="432">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Amplitude scale factor" id="1" value="13000.0"/>
				<val description="Attack time in seconds" id="2" value="0.01"/>
				<val description="Decay time in seconds" id="3" value="0.05"/>
				<val description="Sustain level" id="4" value="0.0"/>
				<val description="Sustain time in seconds" id="5" value="0.0"/>
				<val description="Release time in seconds" id="6" value="0.01"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="32" name="amps mixers/Mixer2" xPos="862" yPos="303">
			<inputs>
				<val description="First audio rate signal" id="0" value="0.0"/>
				<val description="Amplitude multiplicator for in1" id="1" value="1.0"/>
				<val description="Second audio rate signal" id="2" value="0.0"/>
				<val description="Amplitude multiplicator for in2" id="3" value="0.7"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="33" name="effects/Delay" xPos="866" yPos="402">
			<inputs>
				<val description="Audio input" id="0" value="0.0"/>
				<val description="Delay time in seconds" id="1" value="0.3"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="34" name="modulators/SineLfo" xPos="580" yPos="578">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.07"/>
				<val description="Amplitude of LFO" id="1" value="5000.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="35" name="maths/ControlAdd" xPos="686" yPos="540">
			<inputs>
				<val description="First control signal" id="0" value="0.0"/>
				<val description="Second control signal" id="1" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="36" name="sequencing/Sequencer" xPos="113" yPos="115">
			<inputs>
				<val description="Trigger or clock signal" id="0" value="1.0"/>
				<val description="Resets to val1" id="1" value="0.0"/>
				<val description="Number of steps" id="2" value="8.0"/>
				<val description="Value for step 1" id="3" value="50.0"/>
				<val description="Value for step 2" id="4" value="50.0"/>
				<val description="Value for step 3" id="5" value="48.0"/>
				<val description="Value for step 4" id="6" value="48.0"/>
				<val description="Value for step 5" id="7" value="46.0"/>
				<val description="Value for step 6" id="8" value="48.0"/>
				<val description="Value for step 7" id="9" value="50.0"/>
				<val description="Value for step 8" id="10" value="50.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="37" name="modulators/PulseLfo" xPos="12" yPos="112">
			<inputs>
				<val description="Frequency of LFO" id="0" value="0.625"/>
				<val description="Amplitude of LFO" id="1" value="1.0"/>
				<val description="Initial phase of LFO (negativ to skip initialisation)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="38" name="maths/ControlAdd" xPos="231" yPos="231">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="-50.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="39" name="maths/ControlAdd" xPos="358" yPos="18">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="40" name="control/NoteQuantizer" xPos="475" yPos="18">
			<inputs>
				<val description="Input signal" id="0" value="0"/>
				<val description="Select c" id="1" value="1.0"/>
				<val description="Select cis" id="2" value="0.0"/>
				<val description="Select d" id="3" value="1.0"/>
				<val description="Select dis" id="4" value="0.0"/>
				<val description="Select e" id="5" value="1.0"/>
				<val description="Select f" id="6" value="1.0"/>
				<val description="Select fis" id="7" value="0.0"/>
				<val description="Select g" id="8" value="1.0"/>
				<val description="Select gis" id="9" value="0.0"/>
				<val description="Select a" id="10" value="1.0"/>
				<val description="Select ais" id="11" value="1.0"/>
				<val description="Select b" id="12" value="0.0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="12" inputNum="0" outModule="11" outputNum="0"/>
		<connection inModule="13" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="3" inputNum="0" outModule="13" outputNum="0"/>
		<connection inModule="13" inputNum="2" outModule="12" outputNum="0"/>
		<connection inModule="2" inputNum="0" outModule="16" outputNum="0"/>
		<connection inModule="11" inputNum="0" outModule="16" outputNum="0"/>
		<connection inModule="15" inputNum="0" outModule="17" outputNum="0"/>
		<connection inModule="18" inputNum="0" outModule="17" outputNum="0"/>
		<connection inModule="19" inputNum="0" outModule="17" outputNum="0"/>
		<connection inModule="3" inputNum="1" outModule="18" outputNum="0"/>
		<connection inModule="21" inputNum="1" outModule="20" outputNum="0"/>
		<connection inModule="21" inputNum="0" outModule="22" outputNum="0"/>
		<connection inModule="24" inputNum="0" outModule="21" outputNum="0"/>
		<connection inModule="25" inputNum="0" outModule="24" outputNum="0"/>
		<connection inModule="26" inputNum="0" outModule="25" outputNum="0"/>
		<connection inModule="27" inputNum="0" outModule="26" outputNum="0"/>
		<connection inModule="28" inputNum="0" outModule="27" outputNum="0"/>
		<connection inModule="29" inputNum="0" outModule="3" outputNum="0"/>
		<connection inModule="29" inputNum="1" outModule="19" outputNum="0"/>
		<connection inModule="5" inputNum="0" outModule="29" outputNum="0"/>
		<connection inModule="30" inputNum="0" outModule="22" outputNum="0"/>
		<connection inModule="31" inputNum="0" outModule="22" outputNum="0"/>
		<connection inModule="32" inputNum="0" outModule="28" outputNum="0"/>
		<connection inModule="29" inputNum="2" outModule="32" outputNum="0"/>
		<connection inModule="32" inputNum="1" outModule="30" outputNum="0"/>
		<connection inModule="33" inputNum="0" outModule="32" outputNum="0"/>
		<connection inModule="32" inputNum="2" outModule="33" outputNum="0"/>
		<connection inModule="35" inputNum="0" outModule="31" outputNum="0"/>
		<connection inModule="35" inputNum="1" outModule="34" outputNum="0"/>
		<connection inModule="28" inputNum="1" outModule="35" outputNum="0"/>
		<connection inModule="36" inputNum="0" outModule="37" outputNum="0"/>
		<connection inModule="38" inputNum="0" outModule="36" outputNum="0"/>
		<connection inModule="39" inputNum="1" outModule="38" outputNum="0"/>
		<connection inModule="39" inputNum="0" outModule="15" outputNum="0"/>
		<connection inModule="40" inputNum="0" outModule="39" outputNum="0"/>
		<connection inModule="16" inputNum="0" outModule="40" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="36"/>
		<param name="lastModuleId" value="40"/>
	</additionalInfo>
</workspace>

