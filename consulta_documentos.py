
from distutils.log import debug
from conexion import conexion 
from flask import Flask,render_template,json,request
from datetime import date
from datetime import datetime
from diario import VentasDiarias,Totales
import locale


    
def consulta_ventas_almacenes():
    #print(fecha_final)
    try:
        con = conexion.con()
        cursor = con.cursor()
        sql = "select BD_BODEGA, DESCRIPCION_BODEGA, to_char(CANTIDAD,'9,999,999'), to_char(VALORTOTAL,'$9,999,999,999'), to_char(NETO,'$9,999,999,999'),NETO from appalmacenes_viewventaspos"
        sql2 = "select to_char(sum(cantidad),'9,999,999,999'), to_char(sum(valortotal),'$9,999,999,999'), to_char(sum(neto),'$9,999,999,999') from APPALMACENES_VIEWVENTASPOS"
        sql_zona = "select zona , to_char(CANTIDAD,'9,999,999'), to_char(VALORTOTAL,'$9,999,999,999'), to_char(NETO,'$9,999,999,999'),NETO from appalmacenes_viewzonas"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.execute(sql2)
        valores = cursor.fetchall()
        cursor.execute(sql_zona)
        zonas = cursor.fetchall()
        cursor.close()
        con.close()
        ventas =[]
        p = []
        for d in data:
            p = (d[0],d[1],d[2],d[3],d[4],d[5])
            ventas.append(p[:])
        return [ventas,valores,zonas]
    except Exception as e:
        print(f'error conexion bd: {e}')

def ventas_por_fecha(fecha_inicial,fecha_final=datetime.now().strftime("%Y-%m-%d")):
    sql = "select  nvl(upper(prefijo),'Total') , to_char(sum(valor),'$9,999,999,999'), to_char(sum(cantidad),'9,999,999,999')  ,sum(valor) , sum(cantidad) from appalmacenes_viewventasfecha"\
            " where to_date(fecha,'yyyy-mm-dd') between to_date(:fecha1,'yyyy-mm-dd') and to_date(:fecha2,'yyyy-mm-dd') "\
            " group by rollup(prefijo) order by sum(valor)" 
    try:
        con = conexion.con()
        cursor = con.cursor()
        cursor.execute(sql,fecha1=fecha_inicial,fecha2=fecha_final)
        data = cursor.fetchall()
        cursor.close()
        con.close()
        return data
    except Exception as e:
        print(f'error conexion bd: {e}')
        
        
def presupuesto_almacenes(anio , mes1 , mes2):
    sql = " SELECT  to_char(CANTIDAD_AÑO_ANTERIOR,'9,999,999,999'),to_char(NETO_AÑO_ANTERIOR,'$9,999,999,999'), SUCURSAL, NOMBRE_SUCURSAL, CATEGORIA, VENDEDOR, NOMBREVENDEDOR,"\
        " to_char(CANTIDAD,'9,999,999,999'), to_char(NETO,'$9,999,999,999'), to_char(UNIDADES_PRESUPUESTADAS,'9,999,999,999'),"\
        " to_char(VALOR_PRESUPUESTADO,'$9,999,999,999'), to_char(DIFERENCIA_DINERO,'$9,999,999,999'), to_char(DIFERENCIA_UNIDADES,'9,999,999,999'),round(CASE WHEN  PORCENTAJE_VENTA > 3 THEN 1 ELSE PORCENTAJE_VENTA END,3)*100 PORCENTAJE_VENTA,"\
        " to_char(CASE WHEN VENTA_DIARIA > 0 THEN 0 ELSE VENTA_DIARIA END,'$9,999,999,999') VENTA_DIARIA ,round(VALOR_PRESUPUESTADO),round(NETO),round(NETO_AÑO_ANTERIOR)"\
        " FROM ("\
        " SELECT J.NETO_AÑO_ANTERIOR,J.CANTIDAD_AÑO_ANTERIOR,"\
        "  NVL(A.SUCURSAL,PK.SUCURSAL) SUCURSAL,  NVL(NOMBRE_SUCURSAL,PK.DESCSUCUR) NOMBRE_SUCURSAL, "\
        "  nvl(a.categoria,pk.categoria) categoria,"\
        "  nvl(a.vendedor,pk.vendedor) vendedor,"\
        "  UPPER(nvl(a.nom_vendedor,tercerdesc))nombrevendedor,"\
        "  SUM(NVL(CANTIDAD,0)) CANTIDAD, SUM(NVL(NETO,0)) NETO"\
        " ,SUM(NVL(PK.UNIDADES,0)) UNIDADES_PRESUPUESTADAS, SUM(NVL(PK.VALOR,0)) VALOR_PRESUPUESTADO,"\
        "  SUM(NVL(NETO,0))-SUM(NVL(PK.VALOR,0)) DIFERENCIA_DINERO, SUM(NVL(CANTIDAD,0))-SUM(NVL(PK.UNIDADES,0)) DIFERENCIA_UNIDADES,"\
        "  ROUND(SUM(NVL(NETO,0))/DECODE(SUM(NVL(PK.VALOR,0)),0,1,SUM(NVL(PK.VALOR,0))),2) PORCENTAJE_VENTA"\
        " , ROUND((SUM(NVL(NETO,0))-SUM(NVL(PK.VALOR,0)))/TO_NUMBER(LAST_DAY(SYSDATE)-SYSDATE+1)) VENTA_DIARIA"\
        " FROM ("\
        " SELECT TO_CHAR(GRUPO) GRUPO, TO_CHAR(DESCGRUPO) DESCRIPCION_GRUPO ,"\
        " TO_CHAR(subgrupo) SUBGRUPO,TO_CHAR(descsubgrupo) DESCRIPCION_SUBGRUPO,TO_CHAR(AÑO) AÑO , TO_CHAR(MES)MES , "\
        " TO_CHAR(MD_BODEGA) VENDEDOR ,TO_CHAR(DESCRIPCION_BODEGA) NOM_VENDEDOR,'1030' SUCURSAL,"\
        " 'ALMACENES' NOMBRE_SUCURSAL,TO_CHAR(MD_BODEGA) BODEGA,  SUM(NETO) NETO,SUM(CANTIDAD) CANTIDAD ,bd_codigoexterno categoria"\
        "  FROM VENTAS_POS_MP_COLECCION"\
        "  left join bodegas b on bd_bodega = md_bodega"\
        "  WHERE AÑO = :anio AND TO_NUMBER(MES) BETWEEN  :mes1   AND :mes2"\
        "  GROUP BY GRUPO , DESCGRUPO ,subgrupo,descsubgrupo,AÑO , MES , MD_BODEGA  ,DESCRIPCION_BODEGA ,'1030' ,"\
        " 'ALMACENES' ,MD_BODEGA,bd_codigoexterno"\
        " UNION ALL "\
        " SELECT TO_CHAR(GRUPO) GRUPO, TO_CHAR(DESCGRUPO) DESCRIPCION_GRUPO ,"\
        " TO_CHAR(subgrupo) SUBGRUPO,TO_CHAR(descsubgrupo) DESCRIPCION_SUBGRUPO,TO_CHAR(AÑO) AÑO , TO_CHAR(MES)MES , "\
        " TO_CHAR(MD_BODEGA) VENDEDOR ,TO_CHAR(DESCRIPCION_BODEGA) NOM_VENDEDOR,'1030' SUCURSAL,"\
        " 'CONCESIONES' NOMBRE_SUCURSAL,TO_CHAR(MD_BODEGA) BODEGA,  SUM(NETO) NETO,SUM(CANTIDAD) CANTIDAD ,bd_codigoexterno categoria"\
        "  FROM VENTAS_POS_MP_COLECCIONDYJON"\
        "  left join bodegas b on bd_bodega = md_bodega"\
        "  WHERE AÑO = :anio AND TO_NUMBER(MES) BETWEEN  :mes1   AND :mes2"\
        "  GROUP BY GRUPO , DESCGRUPO ,subgrupo,descsubgrupo,AÑO , MES , MD_BODEGA  ,DESCRIPCION_BODEGA ,'1030' ,"\
        " 'CONCESIONES' ,MD_BODEGA,bd_codigoexterno"\
        " ) A"\
        " full JOIN ( "\
        " SELECT "\
        " ANO, MES,CASE WHEN BODEGA = 'TU' THEN '1030' ELSE  TO_CHAR(SUCURSAL) END SUCURSAL, bd_bodega bodega , SUBFAMILIA, GRUPO, "\
        " CASE WHEN BODEGA = 'TU' THEN BODEGA ELSE VENDEDOR END VENDEDOR, UNIDADES, VALOR,SSG.DESCRIPCION SUBFAMILIADESC,SG.DESCRIPCION GRUPO_DESC,"\
        " SS.DESCRIPCION DESCSUCUR,SB.bd_DESCRIPCION BODEGA_DESC,NVL(CASE WHEN BODEGA = 'TU' THEN SB.bd_DESCRIPCION ELSE T.ve_nombre END ,SB.bd_DESCRIPCION) TERCERDESC,sb.bd_codigoexterno categoria"\
        " FROM Presupuesto_ka N "\
        " LEFT JOIN SIKA_SUBGRUPO@SIKA SSG ON SSG.CODIGO =  N.SUBFAMILIA"\
        " LEFT JOIN SIKA_GRUPO@SIKA SG ON SG.ID = SSG.GRUPO_ID"\
        " LEFT JOIN SIKA_SUCURSAL@SIKA SS ON SS.CODIGO  = N.SUCURSAL "\
        " LEFT JOIN bodegas SB ON SB.bd_bodega = N.BODEGA "\
        " LEFT JOIN vendedores  T ON TO_CHAR(T.ve_cedula) = VENDEDOR "\
        " ) PK ON PK.ANO = A.AÑO AND PK.MES = A.MES "\
        " AND PK.SUCURSAL = A.SUCURSAL AND PK.SUBFAMILIA = A.SUBGRUPO AND "\
        " PK.VENDEDOR = A.VENDEDOR AND PK.BODEGA = A.BODEGA "\
        " LEFT JOIN ( "\
        " SELECT CASE WHEN MD_BODEGA = '31' THEN 'TU' ELSE TO_CHAR(MD_BODEGA) END  BODEGA,  SUM(NETO) NETO_AÑO_ANTERIOR,SUM(CANTIDAD) CANTIDAD_AÑO_ANTERIOR "\
        "  FROM VENTAS_POS_MP_COLECCION "\
        "  left join bodegas b on bd_bodega = md_bodega "\
        "  WHERE AÑO = CASE WHEN :anio = 2021 THEN :anio-2 ELSE :anio-1 END AND TO_NUMBER(MES) BETWEEN  :mes1   AND :mes2 "\
        "  GROUP BY MD_BODEGA "\
        " UNION ALL "\
        " SELECT MD_BODEGA , SUM(NETO) NETO_AÑO_ANTERIOR ,SUM(CANTIDAD) CANTIDAD_AÑO_ANTERIOR "\
        "  FROM VENTAS_POS_MP_COLECCIONDYJON "\
        "  left join bodegas b on bd_bodega = md_bodega "\
        "  WHERE AÑO = CASE WHEN :anio = 2021 THEN :anio-2 ELSE :anio-1 END  AND TO_NUMBER(MES) BETWEEN  :mes1  AND :mes2 "\
        "  GROUP BY   MD_BODEGA  "\
        " )J ON J.BODEGA = nvl(a.vendedor,pk.vendedor) "\
        " WHERE  NVL(AÑO,ANO) = :anio AND  to_number(NVL(A.MES,PK.MES)) BETWEEN  :mes1   AND :mes2  and NVL(A.SUCURSAL,PK.SUCURSAL) = '1030' "\
        " GROUP BY NVL(A.SUCURSAL,PK.SUCURSAL),  NVL(NOMBRE_SUCURSAL,PK.DESCSUCUR),nvl(a.vendedor,pk.vendedor) , "\
        "  nvl(a.nom_vendedor,tercerdesc) , nvl(a.categoria,pk.categoria),NETO_AÑO_ANTERIOR,CANTIDAD_AÑO_ANTERIOR"\
        "  )ORDER BY CATEGORIA , PORCENTAJE_VENTA DESC"
    try:
        #print(sql)
        con = conexion.con()
        cursor = con.cursor()
        cursor.execute(sql,anio=anio,mes1=mes1, mes2=mes2)
        data = cursor.fetchall()
        cursor.close()
        con.close()
        #print(sql)
        return data
    except Exception as e:
        print(f'error conexion bd: {e}')
        
def ventasconnombredia(mes, anio):
    sql = """select dia , dia_semana , round(nvl(ecommerce_neto,0)),  
            round(nvl(llano_neto,0)) , round(nvl(cafam_neto,0)), round(nvl(plazaamericas_neto,0)), 
            round(nvl(unicentropalmira_neto,0)), round(nvl(plazacentral_neto,0)), round(nvl(almacen_neto,0)), 
            round(nvl(outlet_neto,0)) , round(nvl(obelisco_neto,0)), round(nvl(pasto_neto,0)), 
            round(nvl(outletbog_neto,0)), round(nvl(carpa_neto,0)), round(nvl(wp_neto,0)) , 
            round(nvl(tulua_neto,0)),round(nvl(septima_neto,0))
            from (select * from  
            (SELECT to_number(TO_CHAR(FECHADOC,'dd')) DIA,TO_CHAR(FECHADOC,'day', 'NLS_DATE_LANGUAGE=SPANISH') dia_semana,upper(MD_BODEGA) bodega,   
            SUM(NETO) NETO 
            FROM VENTAS_POS_MP_COLECCION 
            left join bodegas b on bd_bodega = md_bodega 
             WHERE to_number(to_char(FECHADOC,'yyyy')) = :anio and to_number(to_char(FECHADOC,'mm')) = :mes
            GROUP BY to_number(TO_CHAR(FECHADOC,'dd')) ,TO_CHAR(FECHADOC,'day', 'NLS_DATE_LANGUAGE=SPANISH'),  upper(MD_BODEGA) 
            UNION ALL 
            SELECT to_number(TO_CHAR(FECHADOC,'dd')) DIA,TO_CHAR(FECHADOC,'day', 'NLS_DATE_LANGUAGE=SPANISH') dia_semana,upper(MD_BODEGA) , 
            SUM(NETO) NETO 
            FROM VENTAS_POS_MP_COLECCIONDYJON 
            left join bodegas b on bd_bodega = md_bodega 
            WHERE to_number(to_char(FECHADOC,'yyyy')) = :anio and to_number(to_char(FECHADOC,'mm')) = :mes
            GROUP BY to_number(TO_CHAR(FECHADOC,'dd')) ,TO_CHAR(FECHADOC,'day', 'NLS_DATE_LANGUAGE=SPANISH'),  upper(MD_BODEGA) 
            )pivot (sum(neto) neto 
            for bodega  in ('EC' as ecommerce,'IP' as llano,'19' as cafam,'PA' as plazaamericas,'PL' as unicentropalmira,'PC' as plazacentral,'04' as almacen,
            '61' as outlet,'C6' as obelisco,'UP' as pasto,'79' as outletbog,'CR' as carpa,'WP' as wp,'TU' as tulua,'C7' as septima)   
            ))order by dia """
    try:
        #print(sql)
        con = conexion.con()
        cursor = con.cursor()
        cursor.execute(sql,anio=anio,mes=mes)
        data = cursor.fetchall()
        cursor.close()
        con.close()
        #print(sql)
        ventas = []
        totales = Totales()
        for d in data:
            diaria = VentasDiarias(*d)
            totales.ecommerce += diaria.ecommerce
            totales.llano += diaria.llano
            totales.cafam += diaria.cafam
            totales.plazaamericas += diaria.plazaamericas
            totales.unicentropalmira += diaria.unicentropalmira
            totales.plazacentral += diaria.plazacentral
            totales.almacen += diaria.almacen
            totales.outlet += diaria.outlet
            totales.obelisco += diaria.obelisco
            totales.pasto += diaria.pasto
            totales.outletbog += diaria.outletbog
            totales.carpa += diaria.carpa
            totales.wp += diaria.wp
            totales.tulua += diaria.tulua
            totales.septima += diaria.septima
            ventas.append(diaria)
        return [ventas, totales]
    except Exception as e:
        print(f'error conexion bd: {e}')
                
        
app = Flask(__name__)

# Set the default locale to 'en_US'
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')

# Define the 'currency' filter
@app.template_filter('currency')
def format_currency(value):
    return locale.currency(value, symbol=False, grouping=True)

@app.route('/', methods=['GET','POST'])
def home():       
    ventas_diarias,valores,zonas = consulta_ventas_almacenes()
    #print(ventas_diarias)
    return render_template('ventasdiarias.html',ventas_diarias=ventas_diarias, valores= valores,zonas=zonas)

@app.route('/presupuestos', methods=['GET','POST'])
def presupuesto():
    anio = request.form.get('anio')
    mes1 = request.form.get('mes1')
    mes2 = request.form.get('mes2')
    valor_presupuesto = 0
    valor_venta = 0 
    valor_ano_anterior = 0
    porcentaje_promedio_venta = 0
    if mes1 is None:
        mes1 = datetime.now().strftime("%m")
    if mes2 is None:
        mes2 = datetime.now().strftime("%m")
    if anio is None:
        anio = datetime.now().strftime("%Y") 
    data =  presupuesto_almacenes(anio , mes1 , mes2)
    if data is not None:
        for d in data:
            valor_presupuesto += d[15]
            valor_venta += d[16]
            valor_ano_anterior += d[17] if d[17] else 0
            porcentaje_promedio_venta += d[13]
        porcentaje_promedio_venta = porcentaje_promedio_venta / len(data)
        valor_ano_anterior_str= "{:,}".format(valor_ano_anterior) if str(valor_ano_anterior) != 'None' else 0
        valor_presupuesto_str= "{:,}".format(valor_presupuesto) if str(valor_presupuesto) != 'None' else 0
        valor_venta_str= "{:,}".format(valor_venta) if str(valor_venta) != 'None' else 0
    #print(ventas_diarias)
    return render_template('presupuesto.html',data=data, valor_presupuesto=valor_presupuesto_str, valor_venta=valor_venta_str, valor_ano_anterior=valor_ano_anterior_str, porcentaje_promedio_venta=porcentaje_promedio_venta)

@app.route('/ventasporfecha',methods=['GET','POST'])
def ventasporfecha():
    fecha_inicial = request.form.get('Fecha_Inicial')
    fecha_final = request.form.get('Fecha_Final')
    if fecha_inicial is None:
        fecha_inicial = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if fecha_final is None:
        fecha_final = datetime.now().strftime("%Y-%m-%d")
    data = ventas_por_fecha(fecha_inicial,fecha_final)
    print(f'{fecha_inicial} y {fecha_final}')   
    return render_template('ventas_por_fecha.html',data = data, fecha_final=fecha_final , fecha_inicial = fecha_inicial)


@app.route('/ventaspordia', methods=['GET','POST'])
def ventaspordia():
    mes = request.form.get('mes')
    anio = request.form.get('anio')
    if mes is None:
        mes = datetime.now().strftime("%m")
    if anio is None:
        anio = datetime.now().strftime("%Y")
    datos = ventasconnombredia(mes, anio)
    data = datos[0]
    totals = datos[1]
    return render_template('ventasdiames.html',data=data,mes=mes,anio = anio, totals=totals)
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8002)