import matplotlib.pyplot as plt
import base64
from io import BytesIO

buf = BytesIO()
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig(buf, format='png')
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode('utf-8')
print(img_base64)