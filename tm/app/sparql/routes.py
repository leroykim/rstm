import time
from flask import render_template, flash, request
from app.sparql.forms import SPARQLForm, DataCategoryForm
from app.sparql import bp
from .fuseki import Fuseki
from .query import SyntheaQueryGuiFactory, SyntheaQueryApiFactory

# from .user import UserInfo


@bp.route("/", methods=["GET", "POST"])
@bp.route("/data", methods=["GET", "POST"])
def query_patient():
    form = DataCategoryForm()
    if form.validate_on_submit():
        flash("SPARQL query has been sent.")

        st = time.time()
        query_factory = SyntheaQueryGuiFactory(form=form)
        fuseki = Fuseki()
        query = query_factory.get_select_query()
        result = fuseki.query(query)
        et = time.time()
        elapsed_time = et - st

        # For informations
        # user_info = UserInfo()
        # user_trust_score = f"{user_info.individual_id}'s identity score: {user_info.get_identity_score()} & behavior score: {user_info.get_behavior_score()}, query elapsed time: {elapsed_time} seconds"
        # query_for_html = query.replace("<", "&lt;").replace(">", "&gt;")
    else:
        result = None
        query = None
        query_for_html = None
        user_trust_score = None

    return render_template(
        "sparql/patient.html",
        title="PATIENT DATA",
        form=form,
        result=result,
        query=query_for_html,
        user_trust_score=user_trust_score,
    )


@bp.route("/api", methods=["GET", "POST"])
def query_patient_api():
    # Get parameters
    category = request.args.get("category")
    condition = request.args.get("condition")
    st = time.time()
    query_factory = SyntheaQueryApiFactory(category=category, condition=condition)
    query = query_factory.get_select_query()
    fuseki = Fuseki()
    result = fuseki.query(query, format="json")
    et = time.time()
    elapsed_time = et - st
    total_count = len(result["results"]["bindings"])
    # {"count": total_count, "result": result, "query": query, "elapsed_time": elapsed_time}
    return {"count": total_count, "query": query, "elapsed_time": elapsed_time}


@bp.route("/sparql", methods=["GET", "POST"])
def query_sparql():
    form = SPARQLForm()
    if form.validate_on_submit():
        flash("SPARQL query has been sent.")
        fuseki = Fuseki()
        result = fuseki.query(form.sparql_query.data)
    else:
        result = None
    return render_template("sparql/sparql.html", title="SPARQL", form=form, result=result)


# @bp.route('/setting', methods=['GET', 'POST'])
# @login_required
# def setting():
#     form = SettingForm()
#     return render_template('sparql/setting.html', title='Setting', form=form)
