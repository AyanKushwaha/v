########################################################################

#
"""
RunMacro.py

usage:
 4 different usages:

 A) Runmacro.py "" ""
   Load plan and measure it
   Exit studio

 B) Runmacro.py "" <macro>
   Load plan
   Run <macro> and measure it
   Exit studio
   
 C) Runmacro.py <premacro> <macro>
   Load plan
   Run <premacro>
   Run <macro> and measure it
   Exit studio

 D) Runmacro.py <premacro> <macro> <posmacro>
   Load plan
   Run <premacro>
   Run <macro> and measure it
   Run <posmacro>
   Exit studio
   
 E) Runmacro.py <premacro> STOP
   Load plan
   Run <premacro>
   Leave studio open in order to measure manually


"""
import os
import subprocess
import Cui
import Errlog
import Variable
import Csl
import time

macrospath="../Testing/perftests/"

def getfree(opt=0,flags="-m"):
    # use the 'free' command to determine the available system memory
    # unit = MB
    x=subprocess.Popen("free "+flags, shell="False", stdout=subprocess.PIPE).stdout.readlines()
    mem=int(x[1].split()[3])
    withbuff=int(x[2].split()[3])
    swap=int(x[3].split()[3])
    if opt==0:
          return withbuff+swap
    if opt==1:
          return mem+swap
    return


def my_open():
    #OpenPlan.loadPlan("PERFTIME")
    #OpenPlan.loadPlan()
    PM.PlayMacroFile(macrospath+"InitialLoad")

def getmem(pid,s="size"):
   # unit=MB
   p = subprocess.Popen("ps -p %d -o %s " % ( pid,s ), shell="False", stdout=subprocess.PIPE)
   return int(p.stdout.readlines()[1])/1024

   
 
my_ct = 0
my_t=0
my_sz=0
my_rss=0

def start_clock():
    global my_ct, my_t, my_sz , my_rss
    my_ct = time.clock()
    my_t = time.time()
    my_sz=getfree()
    my_rss=getmem(os.getpid(),"rss")

    Errlog.log("PERFTEST My_Clock:Start, SZ=%d RSS=%d" % (my_sz,my_rss))

def check_clock():
    global my_ct, my_t
    Errlog.log("PERFTEST My_Clock:Check cpu: %.3f s  real: %.3f SYS=%d RSS=%d " % (time.clock() - my_ct,time.time()-my_t,my_sz-getfree(),getmem(os.getpid(),"rss")-my_rss))


if __name__ == '__main__':
    import Csl
    import Gui
    csl = Csl.Csl()
    import carmensystems.studio.MacroRecorder.PlayMacro as PM
    import carmensystems.studio.plans.private.TimeUpdater as TimeUpdater
    import carmensystems.studio.Tracking.OpenPlan as OpenPlan

    pid=os.getpid()


    timeupdater = TimeUpdater.TimeUpdater()
    timeupdater.start("PERFTIME")

    # parse the arguments
    if len(sys.argv)==3:
        premacro=sys.argv[1]
        macro=sys.argv[2]
        posmacro=""
    else:
        if len(sys.argv)==4:
            premacro=sys.argv[1]
            macro=sys.argv[2]
            posmacro=sys.argv[3]
        else:
            macro=""
            premacro=""
            posmacro=""
    #    Errlog.log("PERFTEST Error. Needs 2 arguments. Exiting...")
    #    Cui.CuiExit(Cui.gpc_info,1)

    # do the test
    if macro=="":
        ## only load plan, clock it
        Errlog.log("=========== open plan START ===========PID:%d=======" % (pid,))
        beforeSZ=getfree()
        beforeRSS=getmem(pid,"rss")
        before=time.time()
        beforeCPU=time.clock()
        my_open()
        reltime=time.time()-before
        CPUtime=time.clock()-beforeCPU
        SZ=beforeSZ-getfree()
        RSS=getmem(pid,"rss")-beforeRSS

        Errlog.log("PERFTEST === open plan DONE Real: %.3f s CPU: %.3f s mem SYS: %d m, mem RSS: %d m ==================" % (reltime,CPUtime,SZ,RSS))
        Cui.CuiExit(Cui.gpc_info,1)

    ## if we're here, we are not measuring the load timne,
    ## so just load the plan, don't measure it
        
    Errlog.log("=========== open plan START ==================")
    my_open()
    if premacro<>"":
       ## if we have a premacro, run it
       Errlog.log("=========== running pre-macro %s ==================" % (premacro,))
       PM.PlayMacroFile(macrospath+premacro)

    if macro<>"STOP":
      for n in range(0, 1):
        for n in range(0, 1000):
          ## run macro and measure it
          Errlog.log("=========== running macro %s START (run %d) ==================" % (macro,n))
          beforeSZ=getfree()
          beforeRSS=getmem(pid,"rss")
          before=time.time()
          beforeCPU=time.clock()
      
          #Cui.CuiDisplayObjects(Cui.gpc_info, Cui.CuiArea0, Cui.CrewMode, Cui.CuiShowAll)
          PM.PlayMacroFile(macrospath+macro)
      
          reltime=time.time()-before
          CPUtime=time.clock()-beforeCPU    
          SZ=beforeSZ-getfree()
          RSS=getmem(pid,"rss")-beforeRSS
          s="PERFTEST === macro %s DONE Real: %.3f s  cpu:%.3f s (pre.macro = '%s')=======mem SYS: %d m, mem RSS: %d m===========" % (macro,reltime,CPUtime,premacro,SZ,RSS)
          Errlog.log(s)

        #PM.PlayMacroFile(macrospath+"N2217.RefreshSmallChange")
      
      #PM.PlayMacroFile(macrospath+"PruneToTmpFileRevId")
      
      Cui.CuiExit(Cui.gpc_info,1)
    else:
      ## macro was STOP... just leave studio open.
      Gui.GuiMessage("Please complete test %s manually" % premacro.split(".")[0])
