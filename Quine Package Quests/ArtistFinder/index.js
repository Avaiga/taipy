import React, { Component } from 'react';
import './style.css';
import Music from './component/Music';
import About from './component/About';
import { render } from 'react-dom';
import { BrowserRouter as Router, Switch, Route, Link } from 'react-router-dom';
class App extends Component {
  render() {
    return (
      <Router>
        <nav className="navbar navbar-inverse navbar-fixed-top">
          <div className="container-fluid">
            <div className="navbar-header">
              <Link to="/" className="navbar-brand">
                Artist Finder
              </Link>
              {/* <button className="navbar-toggle" data-target="#menu" data-toggle="collapse">
                <span className="icon-bar"></span>
                <span className="icon-bar"></span>
                <span className="icon-bar"></span>
              </button> */}
            </div>
            {/* <div className="navbar-collapse collapse" id="menu">
              <ul className="nav navbar-nav">
                <li>
                  <Link to="/music">Artist Finder </Link>
                </li>
                <li>
                  <Link to="/about">About </Link>
                </li>
                <li>
                  <Link to="/contact">Contact </Link>
                </li>
              </ul>
            </div> */}
          </div>
        </nav>
        <div className="container">
          <Switch>
            <Route exact path="/" component={Music} />
            <Route exact path="/music" component={Music} />
            <Route exact path="/about" component={About} />
          </Switch>
        </div>
      </Router>
    );
  }
}
export default App;
render(<App />, document.getElementById('root'));
