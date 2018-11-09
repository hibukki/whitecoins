import React, { Component } from 'react';

class Welcome extends React.Component {
  
  onChange(event) {
    this.setState({address: event.target.value});
    console.log("onchange func");
    console.log(event.target.value)
  }

  render() {
    return (<div className="all">
                <div className="search">
                    <h2> search </h2>
                    <form action="" method="GET">
                        <div className="form-group ui-widget">
                            <div className="input-group add-on">
                                <input className="form-control autocomplete" defaultValue="0x23443534" placeholder="Search address..." name="search" onChange={this.onChange.bind(this)}/>
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
                
                    <h2> Here is the dirty info about the address {this.props.address}</h2>
                    <pre>
                        {JSON.stringify(
                              this.props.data_from_api, undefined, 2
                            )
                        }
                    </pre>

                    <h2> Here is the dirty info about the address {this.props.address} from server</h2>
                    <pre>
                        {JSON.stringify(
                              this.props.data, undefined, 2
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
                <div>Hello, {this.props.name}</div>
                <a onClick={() => this.props.foofunc()}> click me! </a>
            </div>);
  }
}

export default Welcome;