import streamlit as st
import folium
import pandas as pd
import requests
from collections import defaultdict
from streamlit_folium import st_folium

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Stelliant — Carte Bas Carbone",
    page_icon="🗺️",
    layout="wide",
)

# ── Stelliant palette ──────────────────────────────────────────
NAVY   = "#002D62"
ORANGE = "#F47920"
SKY    = "#00AEEF"
GREEN  = "#4CAF7D"
MUTED  = "#5A6E84"
BG     = "#F4F7FB"
BORDER = "#D2DCE8"

# ── Logo (base64 embedded so it works without static file serving) ──────
LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCACVAVEDASIAAhEBAxEB/8QAHQABAAMBAQEBAQEAAAAAAAAAAAYHCAUEAgMBCf/EAFEQAAEDAwEEBgUFCQ4EBwAAAAEAAgMEBREGBxIhMQgTFEFRYSJxgZGhFTJCUrEWIzM3YoKSosEkNDhDcnN2lbO0wtHj8BcYJlNVVmR0lLLh/8QAGwEBAAMBAQEBAAAAAAAAAAAAAAQFBgMCAQf/xAA4EQACAQICBwQIBQUBAAAAAAAAAQIDBAUREiExQVFxgQZhkaEiMlKxwdHh8BMUM0JiIyRykvEV/9oADAMBAAIRAxEAPwDZaIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCg1y1gypvcFDT0TJ7Y6pbTS1T2ni9xwNw8gRzz344Y5rq66r5208FloD+7bi7qwR9Bn0nf77s+C8Oo7ZSW22aetFK0MZ8qwce95GS5x8ys9id3XqSlC3eSp5aT4t5ZR8Nb5pb2W9hQpR0ZVVm5Z5dyW2Xy6krt8jpaGCSRwc90bS4jvOOK/dea1YNspSBjMLT7wF6VfU3nBFXUWUmFBNf7TLXpasNuipn3Cuazeexjw1kZ7g53HjjjgA+zK6m0rUzdMabkqYi01s56qlaePpHm7Hg0cfcO9Zs7PXXWpqXRNfUztjkqZnOdx3Wgue8k8/HxXGpXymqcdpquzmA07xO4uf01s3Z9eC9/I0Ps01/R6zZUQ9lNFXU43nwmTfDmE4DmnAz4HhwyPFTNZh2IVklJtRtjWHDapssEnm0xucB+kxvuWnlKayyIfaXDKWHXmhS1Rkk0uG1ZeQREXwzwREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBfx7msYXuIa1oySe4L+qPa9rJIbMKKmGamveIIx5Hn/AJe1Rb26jaW860v2rxe5dXqOtCk61RQW85+kWyXrUVZqWYfeBmCjae5o7/Lh8XFfOuqgu1NZKWPG/E2aoxz9Ld3Y/e7gpTaKKO3WynoYuLYWBucfOPefaclRGSL5V2izSkkxUboYG45EtBlOfU5uPWQqGpaztrKnQk86lSacnxlnpvpqy5Ftb1o1bmdX9sIvLllor35k2jY2ONsbeDWgAeoL6RR/aHehY9KVlU1+7USN6mn8escCAfYMu9i0lSpGlBzexFVQozr1Y047ZPIpba1qA33VExifmko8wQYOQcH0ne0/ABS6m0hHpjZJfK6rhabpVUTnz7wyY2cCIh+3xPjgLgbH9Ni8alFdUxb1Fb8SEEcHSfQb7PneweKsjbXUmm2Z3ZzXYc8RRjjjO9KwH4Eqtw6MqkXXntf39DdYhdKjXt8Lt9icc/FZL4voUXscYZNqliaO6WV3uhkP7FqZZu6PlL2jaVHKW5FNRzS58Cd1n2PK0iriWxFf22qKV/GK3RXvbCIi8mPCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAKLAC7a+JILqe1RcPDrHf7/AFQpFcJXQUFRM0gOjic4E8sgErh7PoCLK6vk4z1sz5ZHd/MgftPtVJiL/MXlC03Zub5RyyX+zT6E23/p0p1d/qrrt8syQVMzKenknkOGRsL3HwAGSors8p5JKV9znb98qnyVBPnI4cPcxp/OXr2hVMsenX0dPxqK+RtLEPHePH4ZHtXXtFLHR0McEQ9BoDW/yQA0fABdJ/18RUd1OOfWT1dUl5nqL/CtG9835L55+R61UO3a5Ge50VoiJLYI+teAM5e7gB6wB+srYrqmKjop6ud27FDG6R58ABkqntIU8msNpMt2qYh2aGTtL2nuxwib8B690rzi9RyULaHrTfkiz7PQjSqTvKi9Gmm+r2L77iyNn9iGn9L0tC9gbUuHW1JHfI7n7uDfUAoh0jK0Q6PpaEEb1TWAkfksa4/buqzlnzpBXcV+sG26M5jt0IYeP8Y8BzvhuD2FWejGlTUI7Nh07PQnfYtGrPXk3J/fNo6nRloXGuvVydG4NZFFAx+7wJJc5wz3/Nb7x4q71CtidodaNn9I2WMxz1T31ErT4k4H6rWqaruyH2huldYjVmtieS6avhmERF8KUIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiKgdiu2zU2ttc0VgulttEFPPBJI99OyQPy1mRjeeR8EBfyIiAIiIAiIgCIiAIiICPa9rjS2R1O0EuqsxDHMDv+HD2rpaepXUNko6V43XxxAPHg7mfiuDqZ3bNXWehxlrMSkePHP2M+Kk9dUx0dHNVTHEcLC93qAys5YzVbErm6k/Rp5QXdklKXmyfVTjQp00tctfwRGa94um0CkpWnMVsjMj8cuscOA9nA+wqVtaGtDW8ABgKMbPKaR1vqLxUt/dFwmdKfJueA9+fYQpQpmDRlOi7ma11W5dHqiv8AVI+XzUZqlHZBZdd/nmQvbBcex6V7Ix2JKyUR8Dx3R6TvsA9q+djVBHTaVNYIyJauVznOIxlrTutA8ufvKi+12qkuOrKe1wemYI2xtaP+5IQfs3Falnoo7baqWgiOW08TYwcc8DifbzUW0k7rFatXdBaK5/eZbXX9rhNKjvqPSfLd8D0SPZHG6SRwaxoLnE8gB3rM9ooZNc7SXCbhDVVT6moz9GEOyW+7DfaFdm127fJOha4scGzVYFLH+f8AO/V3lBujvay+a53hzSWtcylYe7ON93+D3q3qS0qqhwJmBydjh1xe7G/Rj9835FzMa1jAxoDWtGAB3Bf1EUox54hdrU6r7ILnRGo39zqhO3f3uWMZznyXtWYqTZbrmPb4dTu09i0/dHJW9p7TB+BM5cH7u/vcjnGM+S06gCIiAIiIAiIgCIiAIiIAiKg7Rtr1LWbZXaKkttpbQi9z2/rgyTrerjke0H5+N7DR3Y8kBfiIiAIiIDMXSA2q6kq9Yz6K0jU1VHBTSimlfR5FRVTnGWNI9IAEhuG4JIPEjAUYZsX2uSU4uBpnicN3xG66N6/1Z3sA/nL9tuektUaL2nVmsLdBUChmrPlCluEMe8yCQneLX8CGkOz87g4EeYHSsnSW1XTxtbc7LaLkG83ROfA53rOXD3BAfzYxtX1RpvWNPpTWFTWVNDNUikkFcSZ6KUndB3nekW72AQ48BxGMYOrVnnSuqNju03Ve9qHS3ybqKtcwNfPO/q53gBrWtkY4DewABlrc4GMlaGQBf59aGotSXC9U1LpPtvys6Jxi7JP1Mm6G5dh28MDHPiv9BVi/osfjjs3/ALeo/sXID2/cht++rqz+uv8AVT7kNv31dWf11/qrYajl/wBd6OsFxdbr1qS22+rY0PdDPMGuDTyOD3ICRoiICmekFtgk0ZI3TunRFJfJIxJNNI0OZSMPLhyLzzAPADBIOQDTlo0Tth2g04vj5rlNBL6cM9fXmJsme+NhPBvgQ0N8FDr7f+3bRK7Ul0o47g2S5PqH0s7iGSNDzuxux9EANbjwGFa46Tl+AAGmLSAOAAqH/wCSAjdBqzapsiv0VHeu3Pp3cexV8xmgnYOfVSZdunjzYeGRvA8lq3Q+prZq/TFHf7TIXU9S3ix3z4njg5jh3EHh8RwIKyhtL20VevNMvslz03bIfvjZYaiOZxfC9p5tz4jLT5OKm3Qvu83a9RWF0hdAWRVkbc8GvyWPPtHV/ooDSa/jjhpPgF/V/HcGk+S+PYCJUX7p2jVDyMiniIb5YaB/iK/XXk0lU6j09SvxNXSAyY5tjB5/DP5pXi0ZUdr1PcK5xa1ro3OPgAXDB9wXS01E243qt1C5voPPUUufqN4Fw9ZH2rBYbP8AO2cqVN/r1Jt/4Z+k/DKPNou6i/Bqqcv2RWXPd8+hIKaGOmp46eFu7HEwMYPAAYC/QkAEkgAcSSi5+pZeo07cpskblJKeH8krdTlGjTb3Je4p4RdSaW9srDRMZ1BtJlub/Sijkkq+I7s4YPZlp/NVvqt9iVPiO6Ve7wLo4mn1Akj4hWDcKuChoZ62pfuQwRukkPg0DJVL2dho2X4sts25Px+hdY/Nzvfwo7IpRX31KY6QF3NTfKWzxvBio4+skAP8Y/uPqaB+kVYmyi1vtOg7dBLCIppWmeQcckvO8M5793dHljHcqf01RT612iNfVsLo553VVUDxDYgc7vq+az2haKAAAAGAFMsZOtKVZ79hZY/KNnZ0MPjtXpS5/wDW/IIiKyMgZHotSajPSSNuOobwaL7qZIezGul6rq+0OG5ub2N3HDGMLXCxnQ/woj/S2T+8uWzEB8TyxQQvnmkZHFG0ue95w1rQMkk9wWUNp22jVGsL6bDod9bRW58vU0/Y2kVdafrZHpNB5hrcHHM9wubpOXOe2bHLsKZ7mPrHxUhcPqPeN8e1oc32qv8Aoa6dopILzqqaNslXHMKCnLh+CbuNe8jzdvNHqb5lAQR+y3bRSU/y0ylugqAN8iK6g1IHjwfknyBJ8lx79tU13cLFSWOvvFxp6q3zvzVRTvp6h4xu9XLu43i0jmePPOTxW31lnphacpLdqe06hpImRPukUkdUGjG9JFu4efMtfg/yAgLq6P1ZV1+yCw1dfV1FXUyMlL5p5DI92JpAMucSTwACnir3o4fiV07/ADc39vIrCQGTNvettW2TbJdKW2ajulNSU7qd7KWOre2L8ExxG6COBOc+OSvBTU23HaQyS+0ct7lo5XExmOuFHT4zyjYXtDgOW8AeXEkrxdIyJtRt2u0DiQ2V9Kwkc8GGMLZVHTQUdJDSUsLIaeCNscUbBhrGtGAAO4ADCAyBpXaXtD2a6q+S9Ty3KrpopAKy33CQyyNYfpRPcSQccRglrviNe26sprjb6a4UUzZqWpibNDI3k9jgC1w8iCCs7dNOipxLpi4tjaKhwqYHvA4uYOrc0E+RLsfyirT6PU76jYzpt8ji4tp3RjPgyR7QPcAgJ6sJaogu1Vtmv1PYu0fKkmoa1tL2eXq5N/tEmN12Rg+eQt2rGenv4Uj/AOltV/eJEB6fuQ2/fV1Z/XX+qh0ht+x83Vn9df6q2GuFqTWOltN1UVLfr9QW2eVnWRsqJQwubnGRnuygM5/czts+pqX+s/8AURXv/wAU9nP/AJzsv/yWogKqs23280+0Ead1jbLTb6CGslo6yojbIDEWlzQ47ziN3eAyfqklW/X6K0HqGFtXU6asNe2RuW1DaWMucPKRozj2qF7Ztidv1vXOvlprGWq8uYGyl0e9DU45F4HEOxw3hngACDgYpw7Atp8DnUkIt5gceLo7gRGfMggH4ICN7crXpmwbQ6qh0VUONJDEx7hFMZBBU5cSxj8knGGHmSCSO7A27QmZ1FAakYnMbTJw+ljj8VRWybo+x2K70171bXU1dUUrxJT0VMCYWvHFrnucAXYPEDAGQM55K+0AWItm1wi2a7aKd18Y9kFtq5qKqcGklrS10e/jmQMtdw5jktuqp9tWxm367qPlq2VTLZfQwMfI5mYqkAYAkA4hw4APGTgYIOBgCyW3qzutIu4utCbcWb4qu0N6rd8d/OMLGe1m6RbSdsM4sIdLDWzQ2+jeGnMgGGb+D3Elx492Mrsu6PO0YTdT1NoMe/8AhBWnc/lY3c/DKujYtsWoNDVQvd2qo7pfN0tjexmIaUEYO5niXHiN844HAA45AtoDAwEREBifWFHJs424Ty1tvZWUlPcDWRQSsDmVFLI5xwM8Cd0ubnuc3yWqtJw7PtU2eK7WK12KspZBzbRx7zD9V7cZa4eBXztQ2eWDaBamUt1Y+GqgyaWthx1sJPMcfnNOBlp547jgjPlx6PO0C21zzZrhbquI8GzR1Lqd7h+U0jh6t4oC1NtGrNC6BtohpdPaeuF9lc0RUJpY/QZn0nyYbloxnHeTjHAEj2dHvUM+rbXcL7JpGz2KnbIKenloot10+OL+OBloO6PXkdyrPRnRuvVTXsqNYXWmpaTe3pIKJ5kmk8i8gNb6/S/atJ2S12+y2mmtVqpY6SipYxHDFGODQPtPeSeJJJPFAexee6S9Rbaqb6kL3e4FeheW7z09PbZ5KrBi3CC3Gd7PDGO/PJcLmWjRnLPLJPW9i1bT3TWc0iudMx1VVNPb6TLTVxhksg/i48+kfbwHtVmUsEVNTR08LAyONoa0DuAUF2bOAu1Qw83U+R7HD/NT5Y/sJbxWHKtnnJ5rkk28ureb6cEWWL1G62huCj+0aYQ6LuTj9JjWfpODf2qQKI7W5NzR0jM/hJ42/HP7FqMVnoWVaS9l+4j4bDTu6S/kvefnsgp+q0kZsfvipe/3YZ/hXK25XwUtnhscL/v1WRJMB3RNPD3uH6pUi0dLT2rZ/RVVU8RQx0xne49wcS72nj7VS95qavVurd5wd1ldO2KNg49WwkAD2Dj7yqipXVth9G3j60or6+Ow0mGWn5rFKtzU9SDb6rZ4bSy9iFg+T7DJeJ2YqLhgx55thHL3nJ9W6rCXzDHHDCyGJgZGxoa1oHAAcAF9LQUKSo01BbjM393K8uJV5b35bl4BERdiIYzof4UR/pbJ/eXLZiz/AE2xXVUe2c6zdX2c275cfcOrEsnW9WZS8DG5jewfHHmtAICFbcdOVOqtl15tNCzfrOrbPTtHN743h4aPNwaW/nKg+i3tCtulrpW6evtQykoblI2WGpkO6yGcDdIeTyDhujJ4At88rWKpHa5sEotTXKe+aYrIbXcahxfUU8rT2eZ54l/o8WOJ4nAIPPAOSQLnnrKSCidWz1UEVK1u+6Z8gDA3xLjwx5rHvSQ19Ra41dTQ2eQzWm1RvihmxgTSPIMjx+T6LAPUTyK9UPR72kSzClkbaooGng91aTGOPMANJ8+Sld46NddHp+hhtF4o6i7GVz62eqL44gzdG6yNrQ7kc5J4ny5IC0ujh+JXTv8ANzf28isJRbZNpyt0ls9tWnrjLBLVUbZBI+AksO9I5wwSAeTh3KUoDGnSD/H/AHH+fo/7KJbLWdtrOx7WWpdq1XqW1i2Gglkp3N62pLX4YxjXcN097T3rRKAzx01P3jpb+dqfsjVi9HD8Sunf5ub+3kXG6R+z7UWvaWyR2AUZdRPmdN2iYx8HBgGMA5+aVLtj+n7hpbZxaLBdep7ZSMkEvVP3mZdK9wwcDPBwQEtWMtdCXQHSLqbpVwPkhivAugA5ywyv6x275+k9vratmqEbWdmtk2h2yOKue+juFOD2WuiaC+PPNrh9Nh8OHkQgJJZtQ2O82dl3tl1pKmhezf65ko3WjGTvfVI7wcEd6yZ0ktUUOtNpEEGnXCvho4G0UUkJ3hUTF5JDPEZc1oPIkHHDBXTqujZriOsfHTXKwTU55TPmljLh5t6s49WT61aex7YdbNGXGO+XisZd7vGPvG7HuwUxxgloPFzvyjjHcAeKAgf/AC23T/xaH9L/APEWnEQBERAEREAREQBERAEREAREQBEQkAEk4AQAkAEk4A5lcanAvFY2slYDQU7v3M0j8I/kZCPAcQPaV8TyS3uo7NTlzLaw/fpRw64/Vb5eJ/2eyyJjIRDG0MY1u60NHIKmjU/9OpnH9GL2+21w/inv/c9mpa5H6K/k/L6kA005lt1o+lHzHOkgBPhzb9gHtVhKt9bQTUN77fHlgkIkY4fRkbzHvGfapppq9U96oGzRlrZmjE0WeLD/AJHuKz/ZS5ha16+GT1SjJuK4xfDyfJlhiNJ1KcLiOtNZPmdRQrbIf+loB/6xn/0epqSACSQAOJJVXbUtS0Fyp2WqhPXCGYSPnB9DIBG63x58+XrV/j9xTo2M4zlk5LJd55wSjOpeQcVmk833HE1pqPtVjtlhopD2empYu0OB4SSBg9HzA+31Lv7H9KMY1upa5pMxyKNnc1uMF58zkgeXr4Q/Sen6nUV4bSRBzIGYdUS44MZ/meQH7AVfFHTQUdJFS00YjhiYGMYOQA5KnwChUvKru6y1LUunDl7+8v8AG7uFjb/k6D1y1y5Pjz93cfqiItkYoIiIAiIgCIiAIi/OpnhpqeSoqJWQwxNL5JHuAa1oGSSTyCbQlmfoSAMk4CLm0Tprm9lZIyWCjHGCF7S18ng94PEDwYeI5uGcBvSXqSy1HqUdF5BEReTyEREAREQBERAEREAREQBERAEREAREQBERxwCePDwCAIvydM/HoU8r/cPtK/F4uEvAPhpm+I++O+OAPio9S5UfVi5PuXxeS8z0o8T9ayqp6SEzVErY2DvPf6vFc4x1d3J64SUlD3M5SSjz8B5L2U9up4pu0ODp5/8AuynecPV3D2L1qDUtK968rl6NP2U9v+UtWr+K1cXJaj2pxh6u3j8j5ijZFG2OJgYxowGgcAvpEVrGKikkskjkcjUcLOyvmlpTV0xG7UQtbl279dv5Q+z1BVW6UU1c6W3T1EbWuPVSZ3X7vnhXWuJdtLWe5PdLJTuhmdzkhduk+zkfcsf2j7O18QnGtbSSkuOp9Gvdx15rNlxhuIwt841E8n97CqrlebrXU/UVdwqJovqOdwPrxz9q5zaGrqaKpqoIHvgpgDNIBwbkgAZ8eI4K16TQVhheHS9qqQDkNllwP1QF2bnaqefT1VaaeGOGKSB0bGsaAGkjhw9aq7fspe1M6l3PWk8lnm292t7vEuVj9vRajRjqz17l3nA2RuhdpFvVwsjkbO9srgOL3ZyCfYQPYpgq32K3Ahtws8jS1zXdoaMcuTXA+rDfeVZC2GB1VUsKbW5ZeGoosapOnfVE97z8dYREVqVYREQBERAERV5rraA5la/SuiI/ljU8oIxCA6Gj44L5Xn0RjwPqOMjPWjQnWlox+i72d7e2qXE9GC58EuLe5Ex1BfbVYKIVd1rGU7HO3I28XPleeTGNHpPcfAAlcy30Vwv1TDdb9A6kpIyJKS1OIJa4HLZJ8cHPHAhgy1h45c4At5WgNAm0Vp1DqWvffNTSt9KrmO82nHHLIQfmjiRkAeQaDhTpdKjp0no03m+Py+fuOtV06L0aT0n7Xy+e1928iIoxDCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgKk1R12jdobLvAwmlqnGUtH0muP3xnrzxHrarPtN0t91pm1Fvq4qhjmhx3HAlue5w5g+RXj1fYafUVmfQyuEcgO/DLjO48d/q7iqEuEF70pfBvddQV0PFkjDwc3xB5Oafd4+CzbdXCq8so50pvPk3t+/qa62tqWOUIxc9GtBZc1u/79DSaKtNI7U7VLRNi1HVGmqxgF7aZ247z9En7AplR6q03V0jquC+UBga7dc98wZg+B3seKv6VeFVZxZQ3WF3dtJxqU3zyeT5M7KLkXLVGm7bGX11+ttOAM+nUsB92clQXU22/Sduhe21Cpu1QMhoZGY48+bnYOPMAqVTo1Krygsz5bYXeXL/AKVJvvy1eOwtFQvXW03SukXSU1ZWOq7gwfvKlG/ICeW8fms8fSIOOQKqyl13tb2hXB1NpO3Q2y253X1bI8NYe8GZ+QSO/cbnyUz0JsYs9pq/lbUtQb9dHSGU9aD1LXk5J3Txkdkk5fnjxwCrBWdG39K6lr9lbevAnzwujYv++nr9mLzfV7EcGy1W07ajJPKKn7mdL1QDd+NuJHxgnhG7Ac4uzxd6LeAx3g2tozSdi0jaxb7JRthacGWV3pSTHxc7v9XIdwC7gAAAAAA5AIo1xeOqtCC0Y8F8eLIF1fyrLQhFQhwXx4vvYREUMgBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAFz77ZbXfKPst0o46mMcW7ww5h8WuHEH1Ii+SipLKSzR7hUlTkpQeTW9FVaz2V0dBTvraG7TsiGT1UsQeeWeDgR9ipyvZ1cz4853XEZ8cFEUSFKFOqlBZH6h2Uv7i7pSdeWllyJvo7Y/DqeCOtnvrqaIn0oo6QFx/OLv2K1NM7I9FWTckdb3XOob/G1zusH6AAZ8Moisvx6iWipajK45juITrzoOq1FPLJavdln1J3FGyKNscbGsY0Ya1owAPABfSIuJlgiIgCIiAIiIAiIgCIiAIiIAiIgCIiA//9k="

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Barlow', Arial, sans-serif; }
    .stSelectbox label { font-size: 11px !important; font-weight: 700 !important;
                         color: #5A6E84 !important; letter-spacing: 1px;
                         text-transform: uppercase; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background:white;border-radius:10px;padding:12px 20px;
    display:flex;align-items:center;gap:20px;
    border:1px solid #D2DCE8;margin-bottom:16px;
    overflow:visible;box-sizing:border-box;width:100%;
">
  <img src="data:image/png;base64,{LOGO_B64}"
       style="max-height:56px;width:auto;object-fit:contain;display:block;flex-shrink:0" />
  <span style="font-size:11px;color:#5A6E84;letter-spacing:1px;text-transform:uppercase">
    Catalogue Bas Carbone — Visualisation
  </span>
</div>
""", unsafe_allow_html=True)

# ── GeoJSON (cached independently of the catalog) ──────────────
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"
    return requests.get(url).json()

geo_data = load_geojson()

# ── File upload ────────────────────────────────────────────────
st.title("Visualisation Catalogue Stelliant")
uploaded_file = st.file_uploader(
    "Pour accéder aux visualisations, chargez le catalogue en format Excel (.xlsx).",
    type=["xlsx", "xlsm"],
)

if uploaded_file is None:
    st.stop()

# ── Catalog loading & preparation ─────────────────────────────
@st.cache_data
def prepare_catalog(uploaded_file):
    catalog = pd.read_excel(uploaded_file, sheet_name="Catalogue Bas Carbone")
    catalog.columns = catalog.columns.str.strip()
    catalog = catalog.drop(
        columns=["Sélection des filtres", "Rang Occupé?"],
        errors="ignore",
    )

    def get_region(x):
        mapping = {
            "National":             "Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Bretagne, "
                                    "Centre-Val de Loire, Corse, Grand Est, Hauts-de-France, "
                                    "Île-de-France, Normandie, Nouvelle-Aquitaine, Occitanie, "
                                    "Pays de la Loire, Provence-Alpes-Côte d'Azur",
            "Occitanie":            "Occitanie",
            "Ouest de la France":   "Bretagne, Pays de la Loire",
            "Île-de-France":        "Île-de-France",
            "Martinique":           "Martinique",
        }
        return mapping.get(x, "none")

    catalog["Region"] = catalog["Secteur d'intervention /livraison"].apply(get_region)
    return catalog

catalog = prepare_catalog(uploaded_file)

st.dataframe(catalog)

# ── Sidebar filter ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="background:white;border-radius:8px;padding:8px 12px;margin-bottom:12px">
      <img src="data:image/png;base64,{LOGO_B64}"
           style="height:36px;width:auto;object-fit:contain" />
    </div>
    """, unsafe_allow_html=True)

    categories = ["Toutes"] + sorted(catalog["Catégorie"].dropna().unique().tolist())
    categorie_filter = st.selectbox("Filtrer par catégorie", categories)

    st.markdown("---")
    nb_total = (
        len(catalog)
        if categorie_filter == "Toutes"
        else len(catalog[catalog["Catégorie"] == categorie_filter])
    )
    st.metric("Solutions affichées", nb_total)

# ── Map builder ────────────────────────────────────────────────
def build_map(categorie_filter):
    logo_b64_var = LOGO_B64
    filtered = (
        catalog.copy()
        if categorie_filter == "Toutes"
        else catalog[catalog["Catégorie"] == categorie_filter]
    )

    rows = []
    for _, row in filtered.iterrows():
        if row["Region"] == "none":
            continue
        for region in [r.strip() for r in str(row["Region"]).split(",")]:
            rows.append({
                "region":     region,
                "entreprise": row["Entreprise"],
                "categorie":  row["Catégorie"],
                "etat":       row["Etat"],
                "fiche":      row.get("Fiche d'Informations", ""),
            })

    expanded = (
        pd.DataFrame(rows)
        if rows
        else pd.DataFrame(columns=["region", "entreprise", "categorie", "etat", "fiche"])
    )
    count_per_region = (
        expanded.groupby("region").size().reset_index(name="nb_solutions")
        if not expanded.empty
        else pd.DataFrame(columns=["region", "nb_solutions"])
    )

    popup_dict = defaultdict(list)
    for _, row in expanded.iterrows():
        etat_color = {
            "ok":                 GREEN,
            "en cours":           SKY,
            "en attente de test": "#F4A922",
        }.get(row["etat"], MUTED)
        fiche = row.get("fiche", "")
        name_html = (
            f'<a href="{fiche}" target="_blank" '
            f'style="color:{NAVY};font-weight:600;font-size:12px;text-decoration:none;'
            f'border-bottom:1px solid {SKY}">{row["entreprise"]}</a>'
            if fiche and str(fiche).startswith("http")
            else f'<span style="color:{NAVY};font-weight:600;font-size:12px">{row["entreprise"]}</span>'
        )
        popup_dict[row["region"]].append(
            f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0">'
            f'<span style="width:8px;height:8px;border-radius:50%;background:{etat_color};'
            f'flex-shrink:0;display:inline-block"></span>'
            f'{name_html}'
            f'<span style="color:{MUTED};font-size:11px">— {row["categorie"]}</span>'
            f'</div>'
        )

    m = folium.Map(
        location=[46.5, 2.5],
        zoom_start=6,
        tiles="cartodb positron",
        max_bounds=True,
        min_zoom=5,
    )
    m.fit_bounds([[41.0, -5.5], [51.5, 10.0]])

    if not count_per_region.empty:
        choropleth = folium.Choropleth(
            geo_data=geo_data,
            data=count_per_region,
            columns=["region", "nb_solutions"],
            key_on="feature.properties.nom",
            fill_color="Blues",
            fill_opacity=0.75,
            line_opacity=0.4,
            line_color="white",
            legend_name="Nombre de solutions bas carbone",
            nan_fill_color="#EEF3F8",
            nan_fill_opacity=0.5,
        )
        choropleth.add_to(m)
        for child in list(choropleth._children):
            if "color_map" in child:
                del choropleth._children[child]

    for feature in geo_data["features"]:
        nom = feature["properties"]["nom"]
        row = count_per_region[count_per_region["region"] == nom]
        nb  = int(row["nb_solutions"].values[0]) if not row.empty else 0
        details = (
            "".join(popup_dict[nom])
            if nom in popup_dict
            else f'<span style="color:{MUTED};font-size:12px">Aucune solution référencée</span>'
        )
        badge_color = NAVY if nb >= 40 else SKY if nb >= 10 else MUTED

        popup_html = f"""
        <div style="font-family:'Barlow',Arial,sans-serif;min-width:220px;max-width:300px">
          <div style="background:{NAVY};color:white;padding:10px 14px;
                      border-radius:8px 8px 0 0;margin:-1px -1px 0">
            <div style="font-size:14px;font-weight:700">{nom}</div>
            <div style="font-size:11px;opacity:.75;margin-top:2px">Région</div>
          </div>
          <div style="padding:10px 14px;border:1px solid {BORDER};border-top:none;
                      border-radius:0 0 8px 8px;background:white">
            <div style="margin-bottom:10px">
              <span style="background:{badge_color};color:white;padding:3px 10px;
                           border-radius:12px;font-size:12px;font-weight:700">
                {nb} solution{"s" if nb != 1 else ""}
              </span>
            </div>
            <div style="border-top:1px solid {BORDER};padding-top:8px">{details}</div>
          </div>
        </div>
        """

        tooltip_html = f"""
        <div style="font-family:'Barlow',Arial,sans-serif;background:{NAVY};color:white;
                    padding:6px 12px;border-radius:6px;font-size:12px;font-weight:600">
          {nom} &nbsp;·&nbsp;
          <span style="color:{SKY}">{nb} solution{"s" if nb != 1 else ""}</span>
        </div>
        """

        folium.GeoJson(
            feature,
            style_function=lambda x: {"fillOpacity": 0, "color": "transparent", "weight": 0},
            highlight_function=lambda x: {
                "fillColor": ORANGE, "fillOpacity": 0.25, "color": ORANGE, "weight": 2
            },
            tooltip=folium.Tooltip(tooltip_html, sticky=True),
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(m)

    legend_html = f"""
    <div style="position:fixed;bottom:28px;left:28px;background:white;
                border:1px solid {BORDER};border-radius:10px;padding:14px 18px;
                font-family:'Barlow',Arial,sans-serif;
                box-shadow:0 4px 16px rgba(0,45,98,.12);z-index:9999;min-width:180px">
      <div style="margin-bottom:10px;background:white;border-radius:6px;padding:5px 8px;display:inline-block">
        <img src="data:image/png;base64,{logo_b64_var}"
             style="height:28px;width:auto;object-fit:contain;display:block" />
      </div>
      <div style="font-size:10px;font-weight:700;color:{MUTED};letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:8px">Solutions par région</div>
      {''.join([
        f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0">'
        f'<div style="width:14px;height:14px;border-radius:3px;background:{c}"></div>'
        f'<span style="font-size:11px;color:#0D1B2A">{label}</span></div>'
        for c, label in [
            ("#EBF4FC", "0 solution"),
            ("#7AB8E0", "1 – 10"),
            ("#1A5A9A", "11 – 40"),
            (NAVY,      "41 +"),
        ]
      ])}
      <div style="margin-top:10px;padding-top:8px;border-top:1px solid {BORDER};
                  font-size:10px;color:{MUTED}">
        Filtre : <b style="color:{NAVY}">{categorie_filter}</b>
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


# ── Render map ─────────────────────────────────────────────────
st.markdown("### 🗺️ Carte — Couverture géographique")
st_folium(build_map(categorie_filter), use_container_width=True, height=640, returned_objects=[])