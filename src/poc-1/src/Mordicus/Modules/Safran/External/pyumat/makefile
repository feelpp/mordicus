compile :
	f2py umat.f -m py3umat -h umat3.pyf --overwrite-signature
	sed -i '13s/.*/            real*8 dimension(ntens,ntens),intent(in,out),depend(ntens,ntens) :: ddsdde/' umat3.pyf
	f2py -c umat3.pyf umat.f -m py3umat -L${Z7PATH}/PUBLIC/lib-Linux_64 -lZmat_base -lZfem_base -lifcore --build-dir ./build
	echo "Done"

