ادغام کتابخانه‌های FEniCS/OpenFOAM برای مدل‌سازی فیزیکی

ادغام کتابخانه‌های FEniCS (برای روش المان محدود - FEM) و OpenFOAM (برای روش حجم محدود - FVM) برای مدل‌سازی فیزیکی چندزمینه‌ای (Multi-physics) یک چالش پیچیده، اما امکان‌پذیر است. این ادغام معمولاً برای مسائلی مانند Fluid-Structure Interaction (FSI) ، Thermal-Fluid Coupling ، یا Electro-Magneto-Hydrodynamics استفاده می‌شود، جایی که نیاز به حل همزمان معادلات دیفرانسیل با روش‌های مختلف وجود دارد.
در ادامه، روش‌های اصلی ادغام و مراحل کلیدی آن توضیح داده شده است:

۱. استفاده از کتابخانه کوپلینگ PreCICE
PreCICE یک کتابخانه متن‌باز و قدرتمند برای کوپلینگ عددی بین دو یا چند حل‌کننده (Solver) مختلف است. این کتابخانه از FEniCS و OpenFOAM پشتیبانی می‌کند و داده‌ها را بین آن‌ها رد و بدل می‌کند.
مراحل پیاده‌سازی:
1.	نصب PreCICE:
•	ابتدا PreCICE را روی سیستم خود نصب کنید
pip install precice

.2آماده‌سازی حل‌کننده‌ها:
•	FEniCS: کد FEM خود را با استفاده از dolfin یا dolfinx بنویسید و از API PreCICE استفاده کنید.
•	OpenFOAM: از ماژول preciceAdapter در OpenFOAM استفاده کنید (در نسخه‌های جدید OpenFOAM این ابزار وجود دارد).
3پیکربندی PreCICE:
•	یک فایل XML (precice-config.xml) ایجاد کنید که نحوه ارتباط بین دو حل‌کننده را مشخص کند. مثال
<precice-configuration>
  <solver-interface name="Fluid">
    <participant name="OpenFOAM"/>
    <participant name="FEniCS"/>
    <data name="Forces" from="Fluid" to="Solid"/>
    <data name="Displacements" from="Solid" to="Fluid"/>
  </solver-interface>
</precice-configuration>

کدنویسی برای هر حل‌کننده:
در FEniCS
import dolfin
import precice

# مراحل ایجاد مشبندی و تعریف معادلات FEM
# ...

# اتصال به PreCICE
interface = precice.Interface("FEniCS", "precice-config.xml", 0, 1)
mesh_name = "Solid"
interface.set_mesh_vertices(mesh_name, coordinates, vertex_ids)

در OpenFOAM:
•	از preciceAdapter در فایل system/fvSolution فراخوانی کنید.
•	مثلاً برای کوپلینگ حرارتی
#include "preciceAdapter.H"
preciceAdapter::initialize();

5. اجرای همزمان:
•	هر دو حل‌کننده را به صورت موازی اجرا کنید
mpirun -np 2 python3 fenics_solver.py : -np 2 simpleFoam -parallel


۲. روش دستی: ارتباط از طریق فایل یا Pipe

اگر استفاده از PreCICE پیچیده است، می‌توانید داده‌ها را به صورت دستی بین FEniCS و OpenFOAM رد و بدل کنید.
مراحل:
1.	ذخیره خروجی یک حل‌کننده:
•	مثلاً OpenFOAM خروجی خود را در یک فایل CSV یا VTK ذخیره کند.

postProcess -func 'writeCellCentres' -latestTime

2.	خواندن داده در حل‌کننده دیگر:
در FEniCS، داده‌های CSV را بار کنید

import numpy as np
data = np.loadtxt("openfoam_output.csv", delimiter=",")
3.همگام‌سازی زمانی:
اطمینان حاصل کنید که زمان‌های شبیه‌سازی دو حل‌کننده با هم هماهنگ هستند.

۳. استفاده از کتابخانه‌های میان‌افزار (Middleware)
کتابخانه‌هایی مانند HDF5 ، NetCDF ، یا MPI را می‌توان برای انتقال داده‌های مشترک بین FEniCS و OpenFOAM استفاده کرد.
مثال:
در OpenFOAM
// ذخیره داده در HDF5
HDF5::write("data.h5", "velocity", U);
در FEniCS
import h5py
with h5py.File("data.h5", "r") as f:
    velocity = f["velocity"][:]


۴. نمونه مسأله: Fluid-Structure Interaction (FSI)
فرض کنید می‌خواهید جریان سیال (با OpenFOAM) را با تنش سازه (با FEniCS) کوپل کنید:
1.	OpenFOAM فشار و نیروهای سیالی را روی مرزهای جسم سازه‌ای محاسبه می‌کند.
2.	این داده‌ها به FEniCS منتقل می‌شوند.
3.	FEniCS تغییر شکل سازه را محاسبه کرده و به OpenFOAM بازمی‌گرداند.
4.	OpenFOAM مشبندی خود را به روز می‌کند و مراحل تکرار می‌شوند.




چالش‌ها و نکات مهم:

چالش	راهکار
تفاوت در مشبندی (Mesh)	از توابع اینترپولیشن در PreCICE استفاده کنید.
زمان‌بندی ناهمگام	از روش‌های تأخیر زمانی (Time Stepping) هماهنگ استفاده کنید.
هزینه محاسباتی	از MPI برای اجرای موازی استفاده کنید.
پیچیدگی کد	از ماژول‌های آماده (Adapter) استفاده کنید.


