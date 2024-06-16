const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

process.stdin.on('data', (data) => {
    const code = data.toString();
    const ast = parser.parse(code, { sourceType: "module" });

    traverse(ast, {
        VariableDeclaration(path) {
            path.node.declarations.forEach(d => {
                if(d.id.name) {
                    if (d.id.name.includes('sitekey')) {
                        console.log(`Found 'sitekey' in variable declaration`);
                        if (d.init) {
                            let value = d.init.value || (d.init.name ? d.init.name : 'Unable to determine value');
                            console.log(`Sitekey : '${value}'`);
                        }
                    } else if (d.id.name.includes('callback')) {
                        console.log(`Found 'callback' in variable declaration`);
                        if (d.init) {
                            let value = d.init.value || (d.init.name ? d.init.name : 'Unable to determine value');
                            console.log(`Callback : '${value}'`);
                        }
                    }
                }
            });
        },
        
        FunctionDeclaration(path) {
            if (path.node.id.name && (path.node.id.name.includes('sitekey') || path.node.id.name.includes('callback'))) {
                console.log(`Found 'sitekey' or 'callback' in function declaration`);
            }
        },

        MemberExpression(path) {
            if (path.node.property.name && (path.node.property.name.includes('sitekey') || path.node.property.name.includes('callback'))) {
                console.log(`Found 'sitekey' or 'callback' in member expression`);
            }
        },

        ObjectProperty(path) {
            let keyName = path.node.key.name || path.node.key.value;
            if (keyName && (keyName.includes('sitekey') )) {
                console.log("Sitekey :");
                if (path.node.value.type === 'StringLiteral') {
                    console.log(path.node.value.value);
                } else if (path.node.value.name) {
                    console.log(path.node.value.name);
                }
            }

            else if (keyName && (keyName.includes('callback'))) {

                console.log('Callback :');
                if (path.node.value.type === 'StringLiteral') {
                    console.log(path.node.value.value);
                } else if (path.node.value.name) {
                    console.log(path.node.value.name);
                }

            }
        },


        ReturnStatement(path) {
            if (path.node.argument.name && (path.node.argument.name.includes('sitekey') || path.node.argument.name.includes('callback'))) {
                console.log(`Found 'sitekey' or 'callback' in return statement`);
            }
        },

        CallExpression(path) {
            if (path.node.callee.name && (path.node.callee.name.includes('sitekey') || path.node.callee.name.includes('callback'))) {
                console.log(`Found 'sitekey' or 'callback' in function call`);
            }
        },

        AssignmentExpression(path) {
            if(path.node.operator === '=') {
                let leftValue = path.node.left.property ? path.node.left.property.name : '';
                if (leftValue.includes('sitekey') || leftValue.includes('callback')) {
                    console.log(`Found '${leftValue}' in assignment`);
                }
            }
        }
    });
});
