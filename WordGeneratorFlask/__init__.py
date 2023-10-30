import logging

from flask import Flask, render_template, session, request, abort, Blueprint

from pg_shared import prepare_app
from word_generator import PLAYTHING_NAME, Langstrings, core, menu

plaything_root = core.plaything_root

# Using a blueprint is the neatest way of setting up a URL path which starts with the plaything name (see the bottom, when the blueprint is added to the app)
# This strategy would also allow for a single Flask app to deliver more than one plaything, subject to some refactoring of app creation and blueprint addition.
pt_bp = Blueprint(PLAYTHING_NAME, __name__, template_folder='templates')

@pt_bp.route("/")
# Root shows set of index cards, one for each enabled plaything specification. There is no context language for this; lang is declared at specification level.
# Order of cards follows alphanum sort of the specification ids. TODO consider sort by title.
def index():
    core.record_activity("ROOT", None, session, referrer=request.referrer)

    return render_template("index_cards.html", specifications=core.get_specifications(),
                           with_link=True, url_base=plaything_root, initial_view="generate", query_string=request.query_string.decode())

@pt_bp.route("/validate")
# similar output style to root route, but performs some checks and shows error-case specifications and disabled specifications
def validate():
    core.record_activity("validate", None, session, referrer=request.referrer, tag=request.args.get("tag", None))

    def which_assets(detail):  # see core.get_specifications(), which includes exception handling if detail is lacking in specification
        return [m["code"] for m in detail["models"]]
        
    return render_template("index_cards.html",
                           specifications=core.get_specifications(include_disabled=True, check_assets=which_assets, check_optional_assets=["about"]),
                           with_link=False)

@pt_bp.route("/generate/<specification_id>", methods=['GET'])
# view name = "questionnaire", the initial view
def questionnaire(specification_id: str):
    view_name = "generate"

    if specification_id not in core.specification_ids:
        msg = f"Request with invalid specification id = {specification_id} for plaything {PLAYTHING_NAME}"
        logging.warn(msg)
        abort(404, msg)        

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    
    spec = core.get_specification(specification_id)
    langstrings = Langstrings(spec.lang)

    if "models" not in spec.detail:
        msg = f"Missing 'models' in specification id = {specification_id} for plaything {PLAYTHING_NAME}"
        logging.warn(msg)
        abort(404, msg)

    model = None
    prior = ""  # clean page load starts with no prior text
    info = ""
    if "model" in request.args:
        # we have some generation to do
        model = request.args["model"]
        prior = request.args.get("prior", "")
        wg = spec.load_asset_object(model)  # WordGenerator object
        # which button was pressed?
        if "new_word" in request.args:
            prior = wg.generate_word()
        elif "start_word" in request.args:
            prior = wg.generate_start()
        elif "probabilities" in request.args:
            probs = wg.get_options(prior)
            if probs is None:
                info = langstrings.get("NO_OPTION").format(prior=prior)
            else:
                info = ', '.join([(langstrings.get("END") if c == "^" else f"'{c}'") + f": {pc}%" for c, pc in probs.items()])  # TODO? alternatively add a separate parameter to the template and format there.
        elif "add_char" in request.args:
            new_prior = wg.generate_character(prior, append=True)
            if new_prior is None:
                info = langstrings.get("NO_OPTION").format(prior=prior)
            else:
                c = new_prior[-1]
                if c == "^":
                    info = langstrings.get("ADDED").format(c=langstrings.get("END"))
                    prior = new_prior[:-1]
                else:
                    info = langstrings.get("ADDED").format(c=c)
                    prior = new_prior
        if spec.detail.get("capitalize", False):
            prior = prior.title().replace("'S", "'s")  # Python thinks "Adam's" should be title-cased as "Adam'S"
        # else do nothing (should not occur unless someone plays with the URL)

    # note special treatment for tag and menu querystring params. The menu URLs should contain these but NOT the generation form stuff
    menu_arg, tag_arg = None, None
    qs = []
    if "menu" in request.args:
        menu_arg = request.args["menu"]
        qs.append(f"menu={menu_arg}")
    if "tag" in request.args:
        tag_arg = request.args["tag"]
        qs.append(f"tag={tag_arg}")
    return render_template("generate.html",
                           langstrings=langstrings,
                           title=spec.title,
                           instruction=spec.detail.get("instruction", None),
                           menu=menu_arg,
                           tag=tag_arg,
                           models=spec.detail["models"],
                           model=spec.detail["models"][0] if model is None else model,
                           prior=prior,
                           info=info,
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string="&".join(qs)))
        
@pt_bp.route("/about/<specification_id>", methods=['GET'])
def about(specification_id: str):
    view_name = "about"

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    spec = core.get_specification(specification_id)
    if "about" not in spec.asset_map:
        abort(404, "'about' is not configured")

    langstrings = Langstrings(spec.lang)

    return render_template("about.html",
                           about=spec.load_asset_markdown(view_name, render=True),
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))


app = prepare_app(Flask(__name__), url_prefix=plaything_root)
app.register_blueprint(pt_bp, url_prefix=plaything_root)
