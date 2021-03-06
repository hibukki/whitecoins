import React, { Component } from 'react';

class Welcome extends Component {
  
    constructor(props) {
        // Required step: always call the parent class' constructor
        super(props);

        // Set the state directly. Use props if necessary.
        this.state = {
          data:"Nothing searched yet"
        }
    }

  onChange(event) {
    this.setState({address: event.target.value});
    console.log("onchange func");
    console.log(event.target.value)


    const fixed_addr = '1EgV4FoVhCE7gfYhyV7Ryx9357jc44Gm4z'
    fetch('http://142.93.33.226:59876/search_addr/' + event.target.value)
          .then(response => response.json())
          .then(data => this.setState({ data }));
  }

  render() {
    return (<div className="all">
                <div className="search">
                    <h2> search </h2>
                    <form action="" method="GET">
                        <div className="form-group ui-widget">
                            <div className="input-group add-on">
                                <input className="form-control autocomplete" defaultValue="1EgV4FoVhCE7gfYhyV7Ryx9357jc44Gm4z" placeholder="Search address..." name="search" onChange={this.onChange.bind(this)}/>
                                <div className="input-group-btn">
                                    <button className="btn btn-default" type="submit">
                                        <i className="glyphicon glyphicon-search"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
                <div className="mainresult">
                    <h2> Here is the dirty info about the address</h2>
                    <pre>
                        {JSON.stringify(
                              this.state.data, undefined, 2
                            )
                        }
                    </pre>

                </div>

                <div className="footer">
                    <hr/>
                    <h3>
                        When you trade with your friend, you're trading with your friend's friend...
                    </h3>
                    <hr/>
                </div>
            </div>);
  }
}

export default Welcome;