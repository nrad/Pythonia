<?xml version="1.0" encoding="utf-8"?>
<workspace name="external_square_ringmod">
	<referencesModules>
		<moduleReference description="Input for stereo signal from sound card" name="input output/PcmStereoIn">
			<output>
				<vardef csType="a" description="Left input from soundcard" name="left"/>
				<vardef csType="a" description="Right input from soundcard" name="right"/>
			</output>
			<opcode>
				/* Input for stereo signal from sound card */
opcode PcmStereoIn, aa, 0
    aleft, aright  ins
    xout aleft, aright
endop
			</opcode>
		</moduleReference>
		<moduleReference description="Output stereo signal to sound card" name="input output/PcmStereoOut">
			<input>
				<vardef csType="a" description="Audio input left" name="in_l"/>
				<vardef csType="a" description="Audio input right" name="in_r"/>
			</input>
			<opcode>
				/* Output stereo signal to sound card */
opcode PcmStereoOut, 0, aa
  ain_l, ain_r xin
     outs ain_l, ain_r
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
		<moduleReference description="Multiply two audio signals" name="maths/AudioMultiply">
			<input>
				<vardef csType="a" description="First audio signal" name="in1"/>
				<vardef csType="a" description="Second audio signal" name="in2"/>
			</input>
			<output>
				<vardef csType="a" description="Product of input signals" name="pro"/>
			</output>
			<opcode>
				/* Multiply two audio signals */
opcode AudioMultiply, a, aa
  ain1, ain2 xin
  apro = ain1 * ain2
  xout apro
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
		<moduleReference description="Crossfade between two audio signals" name="amps mixers/CrossFader">
			<input>
				<vardef csType="a" description="First audio rate signal" name="in1"/>
				<vardef csType="a" description="Second audio rate signal" name="in2"/>
				<vardef csType="k" description="Crossfade between in1 (fade=0) and in2 (fade=1)" max="1.0" min="0.0" name="fade"/>
			</input>
			<output>
				<vardef csType="a" description="Mixed input signals" name="out"/>
			</output>
			<opcode>
				/* Crossfade between two audio signals */
opcode CrossFader, a, aak
  ain1, ain2, kfade  xin
  kfade  limit  kfade, 0, 1
  aout = ain1*(1-kfade) + ain2*kfade
  xout aout
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="1" name="input output/PcmStereoIn" xPos="64" yPos="33">
			<inputs/>
		</moduleInstance>
		<moduleInstance id="2" name="input output/PcmStereoOut" xPos="572" yPos="49">
			<inputs>
				<val description="Audio input left" id="0" value="0"/>
				<val description="Audio input right" id="1" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="4" name="amps mixers/Amp" xPos="222" yPos="116">
			<inputs>
				<val description="Audio signal" id="0" value="0"/>
				<val description="Gain" id="1" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="maths/AudioMultiply" xPos="322" yPos="5">
			<inputs>
				<val description="First audio signal" id="0" value="1.0"/>
				<val description="Second audio signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="maths/AudioMultiply" xPos="321" yPos="65">
			<inputs>
				<val description="First audio signal" id="0" value="1.0"/>
				<val description="Second audio signal" id="1" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="7" name="control/MidiCtrlIn" xPos="7" yPos="113">
			<inputs>
				<val description="MIDI channel" id="0" value="1.0"/>
				<val description="Controller number" id="1" value="2.0"/>
				<val description="Minimal value for scaled controller" id="2" value="1.0"/>
				<val description="Maximal value for scaled controller" id="3" value="2000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="8" name="control/MidiCtrlIn" xPos="112" yPos="173">
			<inputs>
				<val description="MIDI channel" id="0" value="1.0"/>
				<val description="Controller number" id="1" value="3.0"/>
				<val description="Minimal value for scaled controller" id="2" value="0.0"/>
				<val description="Maximal value for scaled controller" id="3" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="9" name="amps mixers/CrossFader" xPos="454" yPos="8">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Second audio rate signal" id="1" value="0"/>
				<val description="Crossfade between in1 (fade=0) and in2 (fade=1)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="10" name="amps mixers/CrossFader" xPos="453" yPos="84">
			<inputs>
				<val description="First audio rate signal" id="0" value="0"/>
				<val description="Second audio rate signal" id="1" value="0"/>
				<val description="Crossfade between in1 (fade=0) and in2 (fade=1)" id="2" value="0.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="11" name="control/MidiCtrlIn" xPos="328" yPos="139">
			<inputs>
				<val description="MIDI channel" id="0" value="1.0"/>
				<val description="Controller number" id="1" value="1.0"/>
				<val description="Minimal value for scaled controller" id="2" value="0.0"/>
				<val description="Maximal value for scaled controller" id="3" value="1.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="12" name="sound sources/SquareVco" xPos="111" yPos="116">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0"/>
				<val description="Pulse width of square wave" id="1" value="0.5"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="5" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="6" inputNum="0" outModule="1" outputNum="1"/>
		<connection inModule="5" inputNum="1" outModule="4" outputNum="0"/>
		<connection inModule="6" inputNum="1" outModule="4" outputNum="0"/>
		<connection inModule="4" inputNum="1" outModule="8" outputNum="0"/>
		<connection inModule="9" inputNum="1" outModule="5" outputNum="0"/>
		<connection inModule="10" inputNum="1" outModule="6" outputNum="0"/>
		<connection inModule="9" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="10" inputNum="0" outModule="1" outputNum="1"/>
		<connection inModule="2" inputNum="0" outModule="9" outputNum="0"/>
		<connection inModule="2" inputNum="1" outModule="10" outputNum="0"/>
		<connection inModule="9" inputNum="2" outModule="11" outputNum="0"/>
		<connection inModule="10" inputNum="2" outModule="11" outputNum="0"/>
		<connection inModule="12" inputNum="0" outModule="7" outputNum="0"/>
		<connection inModule="4" inputNum="0" outModule="12" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="1"/>
		<param name="lastModuleId" value="12"/>
	</additionalInfo>
</workspace>

