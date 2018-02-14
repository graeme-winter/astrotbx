#include <boost/python.hpp>
#include <scitbx/array_family/tiny_types.h>
#include <scitbx/array_family/small.h>
#include <scitbx/array_family/versa.h>
#include <scitbx/array_family/shared.h>
#include <scitbx/array_family/ref.h>
#include <scitbx/array_family/accessors/c_grid.h>
#include <scitbx/array_family/shared.h>
#include <scitbx/array_family/flex_types.h>
#include <scitbx/array_family/boost_python/flex_wrapper.h>
#include <scitbx/array_family/accessors/c_grid.h>

namespace fractbx {
  namespace ext {

    static scitbx::af::versa< int, scitbx::af::c_grid<2> > make_flex(size_t n)
    {
      scitbx::af::c_grid<2> grid(n, n);
      scitbx::af::versa< int, scitbx::af::c_grid<2> > result(grid, 0);
      return result;
    }

    void init_module()
    {
      using namespace boost::python;
      def("make_flex", make_flex, (arg("size")));
    }

  }
} // namespace fractbx::ext

BOOST_PYTHON_MODULE(fractbx_ext)
{
  fractbx::ext::init_module();
}
