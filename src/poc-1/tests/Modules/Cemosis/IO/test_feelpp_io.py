import sys,os
import pytest
from Mordicus import GetTestDataPath
from os import path as osp

try:
    from Mordicus.Modules.Cemosis.IO import FeelppSolutionReader as FSR
    from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as FMR
    import feelpp
    import spdlog as log
except ImportError:
    pass



cases = [
            ('TestsData/Feelpp/rectangle1',feelpp.create_rectangle,2,1,77),
            ('TestsData/Feelpp/rectangle2',feelpp.create_rectangle,2,2,277),
            ('TestsData/Feelpp/box1',feelpp.create_box, 3,1,245),
            ('TestsData/Feelpp/box2', feelpp.create_box, 3, 2, 1407),
        ]


@pytest.mark.parametrize("dir,case_generator,dim,order,ndofs", cases)
@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_feelpp_generate_data(feelpp_environment, dir, case_generator, dim, order, ndofs):
    feelpp_environment.env.changeRepository(dir)
    mshname,*_ = case_generator()
    feelpp_environment.logger.info("Generating mesh {} with dim: {}, order: {}".format(mshname,dim,order))
    
    mesh = feelpp.load(feelpp.mesh(dim=dim, geo=1, realdim=dim), mshname,0.1)
    Xh=feelpp.functionSpace(mesh, "Pch", order)
    u=Xh.element()
    u.on(range=feelpp.elements(mesh), expr=feelpp.expr("x:x"))
    u.save(path=".",name="u.h5")
    

@pytest.mark.order(after="test_feelpp_generate_data")
@pytest.mark.parametrize("dir,case_generator,dim,order,ndofs", cases)
@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_feelpp_mesh_reader(feelpp_environment, dir, case_generator, dim, order, ndofs):
    feelpp_environment.env.changeRepository(dir)
    mshname, *_ = case_generator()
    feelpp_environment.logger.info("Reading mesh {} with dim: {}, order: {}".format(mshname,dim,order))
    r = FMR.FeelppMeshReader(mshname,dim)
    m = r.ReadMesh()
    assert m.GetDimensionality() == dim


@pytest.mark.order(after="test_feelpp_mesh_reader")
@pytest.mark.parametrize("dir,case_generator,dim,order,ndofs", cases)
@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_feelpp_solution_reader(feelpp_environment, dir, case_generator, dim, order,ndofs):
    feelpp_environment.env.changeRepository(dir)
    mshname, *_ = case_generator()
    feelpp_environment.logger.info("Reading mesh {} with dim: {}, order: {} and solution".format(mshname,dim,order))
    mr = FMR.FeelppMeshReader(mshname,dim)
    m=mr.ReadMesh()
    folder = GetTestDataPath() + "Feelpp/"
    solution_name = "u"

    Xh = feelpp.functionSpace(m.GetInternalStorage(), "Pch", order)
    feelpp_environment.logger.info("space Xh: {}\n".format(Xh.nDof()))
    sr = FSR.FeelppSolutionReader(m, space=Xh)
    s = sr.ReadSnapshotComponent(folder+solution_name+".h5")
    #assert s.shape[0] == ndofs

    sr.WriteSolution(folder+"test", s)
    assert(osp.exists(folder+"test.h5"))
    os.remove(folder+"test.h5")
