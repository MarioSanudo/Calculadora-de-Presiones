from flask import Blueprint, render_template

legal_bp=Blueprint("legal", __name__, url_prefix="/politica")

@legal_bp.route("/aviso-legal", methods=["GET"])
def avisoLegal():
    return render_template("legal/aviso_legal.html")