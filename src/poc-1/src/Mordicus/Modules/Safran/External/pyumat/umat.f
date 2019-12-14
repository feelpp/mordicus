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
      subroutine vumat(
     1   nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     1   stepTime , totalTime , dt, cmname, coordMp , charLength ,
     1   props, density,
     1   strainInc , relSpinInc  ,
     1   tempOld , stretchOld , defgradOld , fieldOld ,
     1   stressOld , stateOld , enerInternOld  , enerInelasOld  ,
     1   tempNew , stretchNew , defgradNew , fieldNew ,
     1   stressNew , stateNew , enerInternNew  , enerInelasNew  )

c
c     Single precision version ONLY ! 
c
      implicit real (a-h,o-z)
      parameter (j_sys_Dimension = 1)
      parameter ( m_vec_Length = 136 )
      parameter(i_ipm_sta = -6)
      character*5 m_ipm_Error
      parameter(m_ipm_Error='Error')
      parameter(m_ipm_Aborted=20)

      dimension coordMp (nblock,*), charLength (nblock), props(nprops),
     1   density(nblock), strainInc (nblock,ndir+nshr),
     2   relSpinInc  (nblock,nshr), tempOld (nblock),
     3   stretchOld (nblock,ndir+nshr),
     4   defgradOld (nblock,ndir+nshr+nshr),
     5   fieldOld (nblock,nfieldv), stressOld (nblock,ndir+nshr),
     6   stateOld (nblock,nstatev), enerInternOld  (nblock),
     7   enerInelasOld  (nblock), tempNew (nblock),
     8   stretchNew (nblock,ndir+nshr),
     9   defgradNew (nblock,ndir+nshr+nshr),
     1   fieldNew (nblock,nfieldv),
     1   stressNew (nblock,ndir+nshr), stateNew (nblock,nstatev),
     2   enerInternNew  (nblock), enerInelasNew  (nblock)

         character*8 cmname


      call zmatexp(nblock,ndir,nshr,nstatev,nfieldv,nprops,lanneal,
     1  stepTime , totalTime , dt, cmname, coordMp , charLength ,                                                                   
     2  props, density,
     3  strainInc , relSpinInc  ,
     4  tempOld , stretchOld , defgradOld , fieldOld ,
     5  stressOld , stateOld , enerInternOld  , enerInelasOld  ,
     6  tempNew , stretchNew , defgradNew , fieldNew ,
     7  stressNew , stateNew , enerInternNew  , enerInelasNew)
                                                                                                                                    
      return                                                                                                                        
      end                                                                                                                           
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


