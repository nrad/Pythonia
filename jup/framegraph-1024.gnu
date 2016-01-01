reset
set terminal png transparent nocrop enhanced
set output 'framegraph-1024-1.png'
set title "Frame time evolution during jack_test run"
set yrange [ 896.00000 : 1152.0000 ] noreverse nowriteback
set xrange [ 0.00000 : 2613.0000 ] noreverse nowriteback
set ylabel "Frametime evolution (d(ft)/dt)"
set xlabel "FrameTime"
set label "| buf.siz:938 | fr.wl:609 | rg.ports:2014 | 2nd.client:1490 | trsprt:0 |" at graph 0.01, 0.04
plot 'framefile-1024.dat' using 2 with impulses title "Xruns",'framefile-1024.dat' using 1 with line title "Sampletime variation at 1024"
set output 'framegraph-1024-2.png'
set title "Frame time evolution during jack_test run"
set yrange [ 512.00000 : 2176.0000 ] noreverse nowriteback
set xrange [ 0.00000 : 2613.0000 ] noreverse nowriteback
set ylabel "Frametime evolution (d(ft)/dt)"
set xlabel "FrameTime"
set label "| buf.siz:938 | fr.wl:609 | rg.ports:2014 | 2nd.client:1490 | trsprt:0 |" at graph 0.01, 0.04
plot 'framefile-1024.dat' using 2 with impulses title "Xruns",'framefile-1024.dat' using 1 with line title "Sampletime variation at 1024"
