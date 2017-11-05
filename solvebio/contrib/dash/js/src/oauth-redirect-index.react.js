/* global window:true, document:true */

import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import cookie from 'cookie';
import queryString from 'query-string';
import {isEmpty} from 'ramda'

require('../styles/application.scss');

const CONFIG = JSON.parse(document.getElementById('_auth-config').textContent);
window.CONFIG = CONFIG;
// const OAUTH_COOKIE_NAME = 'solvebio_oauth_token';
const LOGIN_PATHNAME = '_dash-login';
const IS_AUTHORIZED_PATHNAME = '_is-authorized';

/**
 * OAuth redirect component
 * - Looks for an oauth token in the URL as provided by the SolveBio redirect
 * - Make an API call to dash with that oauth token
 * - In response, Dash will set the oauth token as a cookie
 *   if it is valid
 * Parent is component is responsible for rendering
 * this component in the appropriate context
 * (the URL redirect)
 */
class OauthRedirect extends Component {
    constructor(props) {
        super(props);
        this.state = {
            loginRequest: {},
            authorizationRequest: {}
        }
    }

    componentDidMount() {
        // Support implicit and authorization-code flows.
        const {access_token, code, state} = queryString.parse(window.location.hash || window.location.search);
        this.setState({loginRequest: {status: 'loading'}});
        const {requests_pathname_prefix} = CONFIG;

        window.console.warn(window.location.hash || window.location.search);
        window.console.warn({access_token, code});

        // TODO - Polyfill
        fetch(`${requests_pathname_prefix}${LOGIN_PATHNAME}`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
            },
            credentials: 'same-origin',
            body: JSON.stringify({access_token, code, state})
        }).then(res => {
            this.setState({loginRequest: {status: res.status}});
            return res.json().then(json => {
                this.setState({loginRequest: {
                    status: res.status,
                    content: json
                }});
            }).then(() => {
                return fetch(`${requests_pathname_prefix}${IS_AUTHORIZED_PATHNAME}`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': cookie.parse(document.cookie)._csrf_token
                    }
                }).then(res => {
                    this.setState({
                        authorizationRequest: {
                            status: res.status
                        }
                    });
                })
            });
        }).catch(err => {
            this.setState({loginRequest: {status: 500, content: err}});
        })
    }

    render() {
        const {authorizationRequest, loginRequest} = this.state;
        console.warn(authorizationRequest, loginRequest);
        let content;
        const loading = <div className="_dash-loading">{'Loading...'}</div>;
        if (isEmpty(loginRequest) || loginRequest.status === 'loading') {

            content = loading;

        } else if (loginRequest.status === 200) {

            if (authorizationRequest.status === 403) {
                content = (
                    <div id="dash-auth--authorization__denied">
                        {'You are not authorized to view this app'}
                    </div>
                );
            } else if (authorizationRequest.status === 200) {
                window.close();
            } else {
                content = loading;
            }

        } else {

            content = (
                <div>
                    <h3>{'Yikes! An error occurred trying to log in.'}</h3>
                    <p>Please contact SolveBio Support or try again.</p>
                    <p>Additional information:</p>
                    {
                        loginRequest.content ?
                        <pre>{JSON.stringify(loginRequest.content)}</pre> :
                        null
                    }
                </div>
            );

        }
        return (
            <div>
                {content}
            </div>
        );
    }
}

ReactDOM.render(<OauthRedirect/>, document.getElementById('react-root'));
