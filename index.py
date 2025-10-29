from flask import Flask, render_template, request
import ipaddress

app = Flask(__name__)

def binario_color(ip, mask):
    ip_bin = ''.join([f'{int(octeto):08b}' for octeto in ip.split('.')])
    mask_bin = ''.join([f'{int(octeto):08b}' for octeto in mask.split('.')])
    bits_red = mask_bin.count('1')
    return f"<span class='rojo'>{ip_bin[:bits_red]}</span><span class='verde'>{ip_bin[bits_red:]}</span>"

@app.route("/", methods=["GET", "POST"])
def index():
    data = {}
    if request.method == "POST":
        try:
            ip = request.form["ip"].strip()
            mask = request.form["mask"].strip()

            # Validar IP
            try:
                ipaddress.IPv4Address(ip)
            except:
                data["error"] = "Dirección IP inválida. Usa un formato X.X.X.X"
                return render_template("index.html", data=data)

            # Validar máscara
            try:
                ipaddress.IPv4Address(mask)
            except:
                data["error"] = "Máscara inválida. Usa un formato X.X.X.X"
                return render_template("index.html", data=data)

            # Evitar máscara 0.0.0.0
            if mask == "0.0.0.0":
                data["error"] = "La máscara 0.0.0.0 no es válida. Debe tener al menos un bit de red."
                return render_template("index.html", data=data)

            # Cálculo de red
            red = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            num_hosts = red.num_addresses - 2
            if num_hosts < 0:
                num_hosts = 0  # Evitar negativos para /31 o /32

            rango = "N/A"
            if num_hosts > 0:
                hosts_list = list(red.hosts())
                rango = f"{hosts_list[0]} - {hosts_list[-1]}"

            data["ip_red"] = str(red.network_address)
            data["broadcast"] = str(red.broadcast_address)
            data["hosts"] = num_hosts
            data["rango"] = rango

            # Clase de IP
            primer_octeto = int(ip.split('.')[0])
            if primer_octeto <= 126:
                data["clase"] = "A"
            elif primer_octeto <= 191:
                data["clase"] = "B"
            elif primer_octeto <= 223:
                data["clase"] = "C"
            elif primer_octeto <= 239:
                data["clase"] = "D"
            else:
                data["clase"] = "E"

            # Tipo de IP
            segundo_octeto = int(ip.split('.')[1])
            if (primer_octeto == 10) or (primer_octeto == 172 and 16 <= segundo_octeto <= 31) or (primer_octeto == 192 and segundo_octeto == 168):
                data["tipo"] = "Privada"
            else:
                data["tipo"] = "Pública"

            data["binario"] = binario_color(ip, mask)

        except Exception as e:
            data["error"] = f"Error al procesar la dirección IP o máscara: {e}"

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
