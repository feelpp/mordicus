      subroutine getoutdir(OUTDIR, LENOUTDIR) 
      LENOUTDIR = 0
      return
      end 


      subroutine umat(stress,statev,ddsdde,sse,spd,scd,                                                                             
     1 rpl,ddsddt,drplde,drpldt,stran,dstran,                                                                                       
     2 time,dtime,temp,dtemp,predef,dpred,cmname,ndi,nshr,                                                                          
     3 ntens,nstatv,props,nprops,coords,drot,pnewdt,celent,                                                                         
     4 dfgrd0,dfgrd1,noel,npt,kslay,kspt,kstep,kinc)                                                                         
                                                                                                                                    
      implicit real*8(a-h,o-z)                                                                                                      
      parameter (nprecd=2)                                                                                                          
                                                                                                                                    
      character*8 cmname                                                                                                            
      dimension stress(ntens),statev(nstatv),                                                                                       
     1 ddsdde(ntens,ntens),ddsddt(ntens),drplde(ntens),                                                                             
     2 stran(ntens),dstran(ntens),time(2),predef(1),dpred(1),                                                                       
     3 props(nprops),coords(3),drot(3,3),                                                                                           
     4 dfgrd0(3,3),dfgrd1(3,3)                                                                                                      
      common/count/kiter,kitgen                                                                                                     
     
c     print *,'eto: ',stran(1),stran(2),stran(3),stran(4)
c     print *,'deto:',dstran(1),dstran(2),dstran(3),dstran(4)
                                                                                                                             
      call zebaba(stress,statev,ddsdde,sse,spd,scd,                                                                                 
     1  rpl,ddsddt,drplde,drpldt,                                                                                                   
     2  stran,dstran,time,dtime,temp,dtemp,predef,dpred,cmname,                                                                     
     3  ndi,nshr,ntens,nstatv,props,nprops,coords,drot,                                                                             
     4  pnewdt,celent,dfgrd0,dfgrd1,noel,npt,layer,kspt,kstep,                                                                      
     5  kinc,kiter,kitgen)                                                                                                          
c     print *,'sig:',stress(1),stress(2),stress(3),stress(4)
      return                                                                                                                        
      end                                                                                                                           
                                                                                                                                    
c---------------------------------------------------------------------------- 
c      subroutine vumat(
c     1   nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
c     1   stepTime , totalTime , dt, cmname, coordMp , charLength ,
c     1   props, density,
c     1   strainInc , relSpinInc  ,
c     1   tempOld , stretchOld , defgradOld , fieldOld ,
c     1   stressOld , stateOld , enerInternOld  , enerInelasOld  ,
c     1   tempNew , stretchNew , defgradNew , fieldNew ,
c     1   stressNew , stateNew , enerInternNew  , enerInelasNew  )
c
cc
cc     Single precision version ONLY ! 
cc
c      implicit real (a-h,o-z)
c      parameter (j_sys_Dimension = 1)
c      parameter ( m_vec_Length = 136 )
c      parameter(i_ipm_sta = -6)
c      character*5 m_ipm_Error
c      parameter(m_ipm_Error='Error')
c      parameter(m_ipm_Aborted=20)
c
c      dimension coordMp (nblock,*), charLength (nblock), props(nprops),
c     1   density(nblock), strainInc (nblock,ndir+nshr),
c     2   relSpinInc  (nblock,nshr), tempOld (nblock),
c     3   stretchOld (nblock,ndir+nshr),
c     4   defgradOld (nblock,ndir+nshr+nshr),
c     5   fieldOld (nblock,nfieldv), stressOld (nblock,ndir+nshr),
c     6   stateOld (nblock,nstatev), enerInternOld  (nblock),
c     7   enerInelasOld  (nblock), tempNew (nblock),
c     8   stretchNew (nblock,ndir+nshr),
c     9   defgradNew (nblock,ndir+nshr+nshr),
c     1   fieldNew (nblock,nfieldv),
c     1   stressNew (nblock,ndir+nshr), stateNew (nblock,nstatev),
c     2   enerInternNew  (nblock), enerInelasNew  (nblock)
c
c         character*8 cmname
c
c
c      call zmatexp(nblock,ndir,nshr,nstatev,nfieldv,nprops,lanneal,
c     1  stepTime , totalTime , dt, cmname, coordMp , charLength ,                                                                   
c     2  props, density,
c     3  strainInc , relSpinInc  ,
c     4  tempOld , stretchOld , defgradOld , fieldOld ,
c     5  stressOld , stateOld , enerInternOld  , enerInelasOld  ,
c     6  tempNew , stretchNew , defgradNew , fieldNew ,
c     7  stressNew , stateNew , enerInternNew  , enerInelasNew)
c                                                                                                                                    
c      return                                                                                                                        
c      end                                                                                                                           
c----------------------------------------------------------------------------
      subroutine uexternaldb(
     1   lop, lrestart, time, dtime, kstep,kinc)

      implicit real (a-h,o-z)
      character xodir*255
      dimension time(2)

      if (lop.eq.0) then 
           lxoutdir = 0
           xodir  =' '
           call getoutdir(xodir, lxoutdir) 
           call zmatod(lxoutdir, xodir); 
c          print *,'odir: ',odir
      end if

      call zextdb(lop,lrestart,time,dtime,kstep,kinc)

      return
      end                                                                                                        


