<?xml version="1.0" encoding="utf-8"?>
<workspace name="fm_basic">
	<referencesModules>
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
	</referencesModules>
	<instancesModules>
		<moduleInstance id="1" name="sound sources/SineVco" xPos="31" yPos="24">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="100.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="2" name="sound sources/SineVco" xPos="340" yPos="125">
			<inputs>
				<val description="Frequency of oscillator" id="0" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="3" name="amps mixers/Amp" xPos="123" yPos="27">
			<inputs>
				<val description="Audio signal" id="0" value="0"/>
				<val description="Gain" id="1" value="100.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="4" name="amps mixers/Amp" xPos="473" yPos="127">
			<inputs>
				<val description="Audio signal" id="0" value="0"/>
				<val description="Gain" id="1" value="20000.0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="5" name="input output/PcmMonoOut" xPos="566" yPos="127">
			<inputs>
				<val description="Audio input" id="0" value="0"/>
			</inputs>
		</moduleInstance>
		<moduleInstance id="6" name="maths/ControlAdd" xPos="211" yPos="116">
			<inputs>
				<val description="First control signal" id="0" value="0"/>
				<val description="Second control signal" id="1" value="300.0"/>
			</inputs>
		</moduleInstance>
	</instancesModules>
	<connections>
		<connection inModule="3" inputNum="0" outModule="1" outputNum="0"/>
		<connection inModule="4" inputNum="0" outModule="2" outputNum="0"/>
		<connection inModule="5" inputNum="0" outModule="4" outputNum="0"/>
		<connection inModule="6" inputNum="0" outModule="3" outputNum="0"/>
		<connection inModule="2" inputNum="0" outModule="6" outputNum="0"/>
	</connections>
	<additionalInfo>
		<param name="actualModule" value="3"/>
		<param name="lastModuleId" value="6"/>
	</additionalInfo>
</workspace>

