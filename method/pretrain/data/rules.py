import re


def java(text):
    text = delete_comment(text)
    text = process_dot(text)
    text = merge_redundant_symbol(text)
    return format_text(text)


def english(text):
    pass


def delete_comment(code):
    code = re.sub(r"//.*", '', code)
    code = re.sub(r"/\*.*\*/", '', code, flags=re.S)
    return code


def process_dot(code):
    return code.replace(".", " . ")


def delete_symbol(code):
    sym_list = [".", ";", "(", ")", "[", "]", "{", "}", "'", "\""]
    for symbol in sym_list:
        code = code.replace(symbol, " ")
    code = " ".join(code.split())
    return code


def replace_enter(text):
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    return text


def merge_redundant_symbol(text):
    symbol_list = [
        [["(", "[", "{"], "("],
        [["}", "]", ")", "\n", "\r", ";"], ")"]
    ]
    for symbols, replace_symbol in symbol_list:
        for sym in symbols:
            text = text.replace(sym, " "+replace_symbol+" ")
        tokens = text.split()
        for idx, token in enumerate(tokens):
            if token == replace_symbol:
                i = idx+1
                while i < len(tokens) and tokens[i] == replace_symbol:
                    tokens[i] = ""
                    i += 1
        text = " ".join(tokens)

    tokens = text.split()
    for idx, token in enumerate(tokens):
        if token == "(" and idx+1 < len(tokens) and tokens[idx+1] == ")":
            tokens[idx] = "()"
            tokens[idx+1] = ""
    text = " ".join(tokens)
    return text


def format_text(text):
    text = " ".join(text.split())
    if text == "":
        return " "
    return text


if __name__ == "__main__":
    string = """The <code>key</code> parameter <em>should</em> specify a unique entity across all 4 supported\ntypes: people, groups, portlets, and categories.\n\n<p>Concrete examples of working keys:\n\n<ul>\n<li>admin (user)\n<li>local.0 (group)\n<li>PORTLET_ID.82 (portlet)\n<li>local.1 (category)\n</ul> @Override\n    public IPermissionTarget getTarget(String key) {\n\n        /*\n         * If the specified key matches one of the "all entity" style targets,\n         * just return the appropriate target.\n         */\n        switch (key) {\n            case IPermission.ALL_CATEGORIES_TARGET:\n                return ALL_CATEGORIES_TARGET;\n            case IPermission.ALL_PORTLETS_TARGET:\n                return ALL_PORTLETS_TARGET;\n            case IPermission.ALL_GROUPS_TARGET:\n                return ALL_GROUPS_TARGET;\n                // Else just fall through...\n        }\n\n        /*\n         * Attempt to find a matching entity for each allowed entity type.  This\n         * implementation will return the first entity that it finds. If the\n         * portal contains duplicate entity keys across multiple types, it's\n         * possible that this implementation would demonstrate inconsistent\n         * behavior.\n         */\n        for (TargetType targetType : allowedTargetTypes) {\n            JsonEntityBean entity = groupListHelper.getEntity(targetType.toString(), key, false);\n            if (entity != null) {\n                IPermissionTarget target =\n                        new PermissionTargetImpl(entity.getId(), entity.getName(), targetType);\n                return target;\n            }\n        }\n\n        return null;\n    }
/*\n(non-Javadoc)\n@see org.apereo.portal.permission.target.IPermissionTargetProvider#searchTargets(java.lang.String) @Override\n    public Collection<IPermissionTarget> searchTargets(String term) {\n\n        // Initialize a new collection of matching targets.  We use a HashSet\n        // implementation here to prevent duplicate target entries.\n        Collection<IPermissionTarget> matching = new HashSet<IPermissionTarget>();\n\n        /*\n         * Attempt to find matching entities for each allowed entity type.\n         * Any matching entities will be added to our collection.\n         */\n        for (TargetType targetType : allowedTargetTypes) {\n            Set<JsonEntityBean> entities = groupListHelper.search(targetType.toString(), term);\n            for (JsonEntityBean entity : entities) {\n                IPermissionTarget target =\n                        new PermissionTargetImpl(entity.getId(), entity.getName(), targetType);\n                matching.add(target);\n            }\n        }\n\n        if (IPermission.ALL_CATEGORIES_TARGET.contains(term)) {\n            matching.add(ALL_CATEGORIES_TARGET);\n        } else if (IPermission.ALL_PORTLETS_TARGET.contains(term)) {\n            matching.add(ALL_PORTLETS_TARGET);\n        } else if (IPermission.ALL_GROUPS_TARGET.contains(term)) {\n            matching.add(ALL_GROUPS_TARGET);\n        }\n\n        // return the list of matching targets\n        return matching;\n    }"""
    print(string)
    print(java(string))

