import json,collections,math,sys
from email.utils import parsedate_to_datetime
base=sys.argv[1]
pts=json.load(open(base+"/Bridge As Built 2026/Bridge_Raw_AsBuilt_20261117.geojson"))
rch=json.load(open(base+"/Bridge As Built 2026/Bridge Creek Reaches.geojson"))
def dp(ptsl,tol):
    if len(ptsl)<3: return ptsl
    a,b=ptsl[0],ptsl[-1]; dmax=0; idx=0
    ax,ay=a; bx,by=b; L=math.hypot(bx-ax,by-ay)
    for i in range(1,len(ptsl)-1):
        px,py=ptsl[i]
        d=abs((bx-ax)*(ay-py)-(ax-px)*(by-ay))/L if L else math.hypot(px-ax,py-ay)
        if d>dmax: dmax=d; idx=i
    if dmax>tol:
        return dp(ptsl[:idx+1],tol)[:-1]+dp(ptsl[idx:],tol)
    return [a,b]
TOL=0.000004  # ~0.4 m
def simp(geom):
    polys=geom["coordinates"] if geom["type"]=="MultiPolygon" else [geom["coordinates"]]
    out=[]
    for poly in polys:
        rings=[]
        for ring in poly:
            r=dp([[round(x,6),round(y,6)] for x,y,*_ in ring],TOL)
            if len(r)>=4: rings.append(r)
        if rings: out.append(rings)
    return {"type":"MultiPolygon","coordinates":out}
def inring(x,y,ring):
    c=False; n=len(ring); j=n-1
    for i in range(n):
        xi,yi=ring[i]; xj,yj=ring[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def inmp(x,y,g):
    for poly in g["coordinates"]:
        if inring(x,y,poly[0]) and not any(inring(x,y,h) for h in poly[1:]): return True
    return False
keep=["Reach_Name","Treatment_Type","Channel_Length","Valley_Length","Confinement","Channel_Gradient","Elevation_Change","Estimated_BDA","Estimated_PALS","Design_Narrative","Risk_Description","Reach_Description"]
R=[]
for f in rch["features"]:
    p={k:f["properties"].get(k) for k in keep}
    R.append({"type":"Feature","properties":p,"geometry":simp(f["geometry"])})
short={"Wood Jam (PALS and ALS)":"PALS / Wood Jam","Seeding (felling, grip hoist, brush, rootwad, etc.)":"Wood Seeding"}
P=[];miss=0
for f in pts["features"]:
    p=f["properties"]; x,y=f["geometry"]["coordinates"][:2]
    reach=None; near=None
    for r in R:
        if inmp(x,y,r["geometry"]): reach=r["properties"]["Reach_Name"];break
    if reach is None:
        # nearest reach by vertex distance
        best=1e9
        for r in R:
            for poly in r["geometry"]["coordinates"]:
                for vx,vy in poly[0]:
                    d=(vx-x)**2+(vy-y)**2
                    if d<best: best=d;bn=r["properties"]["Reach_Name"]
        dist=math.sqrt(best)*111000*0.85; miss+=1
        reach=bn if dist<=15 else None
        near=bn
        print("outside reach, nearest",bn,round(dist),"m",file=sys.stderr)
    dt=parsedate_to_datetime(p["CreationDate"]).date().isoformat()
    P.append({"type":"Feature","geometry":{"type":"Point","coordinates":[round(x,6),round(y,6)]},"properties":{
      "id":p["objectid"],"type":short.get(p["structure_type"],p["structure_type"]),"tier2":p["structure_type_tier_2_optional"],
      "maint":p["maintenance_structure_required"],"posts":p["number_of_posts_optional"],"notes":p["notes_optional"],"date":dt,"reach":reach,"near":near if reach is None else None}})
print("outside",miss,file=sys.stderr)
c=collections.Counter((q["properties"]["reach"],q["properties"]["type"]) for q in P)
for k,v in sorted(c.items(),key=str): print(k,v,file=sys.stderr)
print(collections.Counter(q["properties"]["date"] for q in P),file=sys.stderr)
print("posts total",sum(q["properties"]["posts"] or 0 for q in P),file=sys.stderr)
json.dump({"generated":"2026-11-17","reaches":{"type":"FeatureCollection","features":R},"structures":{"type":"FeatureCollection","features":P}},open(sys.argv[2],"w"),separators=(",",":"))
