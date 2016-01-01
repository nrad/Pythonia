<workspace name="01_saw_amp_monoout"><referencesModules><moduleReference description="Saw oscillator (aplitude 1)" name="sound sources/SawVco"><input><vardef csType="k" description="Frequency of oscillator" min="0.0" name="frq"/><vardef csType="k" description="Shape of wave, sawtooth/triangle/ramp" max="0.999" min="0.001" name="shape"/></input><output><vardef csType="a" description="Output of oscillator (amplitude 1)" name="out"/></output><opcode>/* Saw oscillator */
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
  </opcode></moduleReference></referencesModules><instancesModules><moduleInstance id="1" name="sound sources/SawVco" xPos="20" yPos="20"><inputs><val description="Frequency of oscillator" id="0" value="200.0"/><val description="Shape of wave, sawtooth/triangle/ramp" id="1" value="0.001"/></inputs></moduleInstance><moduleInstance id="2" name="amps mixers/Amp" xPos="146" yPos="21"><inputs><val description="Audio signal" id="0" value="0"/><val description="Gain" id="1" value="25000.0"/></inputs></moduleInstance><moduleInstance id="3" name="input output/PcmMonoOut" xPos="257" yPos="20"><inputs><val description="Audio input" id="0" value="0"/></inputs></moduleInstance></instancesModules><connections><connection inModule="2" inputNum="0" outModule="1" outputNum="0"/><connection inModule="3" inputNum="0" outModule="2" outputNum="0"/></connections><additionalInfo><param name="actualModule" value="2"/><param name="lastModuleId" value="3"/></additionalInfo></workspace>